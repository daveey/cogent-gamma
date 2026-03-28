"""CvC PolicyCoglet: CodeLet with LLM brain + Python fast policy.

Submitted to cogames as a MultiAgentPolicy. Each episode:
1. Python heuristic (CogletAgentPolicy) handles every step — fast path
2. LLM brain analyzes game state ~20 times per episode — slow path
3. On episode end, writes learnings/experience to disk for Coach to read

Coach (Claude Code) reads learnings across games and commits improvements.
"""
from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any

from cvc.policy.anthropic_pilot import CogletBasePolicy, CogletAgentPolicy
from cvc.policy.semantic_cog import SharedWorldModel
from mettagrid.policy.policy import AgentPolicy
from mettagrid.policy.policy_env_interface import PolicyEnvInterface

_ELEMENTS = ("carbon", "oxygen", "germanium", "silicon")
_LLM_INTERVAL = 500  # call LLM every N steps (10000/500 = 20 per episode)
_LEARNINGS_DIR = os.environ.get("COGLET_LEARNINGS_DIR", "/tmp/coglet_learnings")


def _build_game_summary(agents: dict[int, CogletAgentPolicy]) -> dict[str, Any]:
    """Collect end-of-game summary from all agents."""
    summary: dict[str, Any] = {"agents": {}}
    for aid, agent in agents.items():
        agent_info: dict[str, Any] = {
            "steps": agent._step_index,
        }
        if agent._infos:
            agent_info["last_infos"] = dict(agent._infos)
        summary["agents"][aid] = agent_info
    return summary


class CogletPolicy(CogletBasePolicy):
    """PolicyCoglet: Python heuristic + LLM brain.

    Fast path: CogletAgentPolicy handles every step.
    Slow path: LLM guides strategy ~20 times per episode.
    End: writes learnings for Coach.
    """
    short_names = ["coglet", "coglet-policy"]
    minimum_action_timeout_ms = 30_000

    def __init__(self, policy_env_info: PolicyEnvInterface, device: str = "cpu", **kwargs: Any):
        super().__init__(policy_env_info, device=device, **kwargs)
        self._llm_client = None
        self._llm_log: list[dict[str, Any]] = []
        self._episode_start = time.time()
        self._game_id = kwargs.get("game_id", f"game_{int(time.time())}")
        self._init_llm()

    def _init_llm(self) -> None:
        """Initialize Anthropic client if API key is available."""
        api_key = os.environ.get("COGORA_ANTHROPIC_KEY")
        if not api_key:
            return
        try:
            import anthropic
            self._llm_client = anthropic.Anthropic(api_key=api_key)
        except ImportError:
            pass

    def agent_policy(self, agent_id: int) -> AgentPolicy:
        if agent_id not in self._agent_policies:
            self._agent_policies[agent_id] = CogletBrainAgentPolicy(
                self.policy_env_info,
                agent_id=agent_id,
                world_model=SharedWorldModel(),
                shared_claims=self._shared_claims,
                shared_junctions=self._shared_junctions,
                llm_client=self._llm_client,
                llm_log=self._llm_log,
            )
        return self._agent_policies[agent_id]

    def reset(self) -> None:
        # Write learnings before reset (end of episode)
        if self._agent_policies:
            self._write_learnings()
        self._llm_log.clear()
        self._episode_start = time.time()
        super().reset()

    def _write_learnings(self) -> None:
        """Write episode learnings/experience to disk for Coach."""
        learnings_dir = Path(_LEARNINGS_DIR)
        learnings_dir.mkdir(parents=True, exist_ok=True)

        game_summary = _build_game_summary(self._agent_policies)
        learnings = {
            "game_id": self._game_id,
            "duration_s": round(time.time() - self._episode_start, 1),
            "summary": game_summary,
            "llm_log": self._llm_log,
        }

        path = learnings_dir / f"{self._game_id}.json"
        path.write_text(json.dumps(learnings, indent=2, default=str))


class CogletBrainAgentPolicy(CogletAgentPolicy):
    """Agent policy with LLM brain that guides strategy mid-game.

    Every _LLM_INTERVAL steps, calls Claude to analyze game state.
    Logs analysis for Coach to review post-game.
    """

    def __init__(
        self,
        policy_env_info: PolicyEnvInterface,
        *,
        agent_id: int,
        world_model: SharedWorldModel,
        shared_claims: dict,
        shared_junctions: dict,
        llm_client: Any = None,
        llm_log: list | None = None,
    ) -> None:
        super().__init__(
            policy_env_info,
            agent_id=agent_id,
            world_model=world_model,
            shared_claims=shared_claims,
            shared_junctions=shared_junctions,
        )
        self._llm = llm_client
        self._llm_log = llm_log if llm_log is not None else []
        self._last_llm_step = 0
        self._llm_interval = _LLM_INTERVAL
        self._llm_latencies: list[float] = []

    def step(self, obs: Any) -> Any:
        action = super().step(obs)

        # LLM brain: analyze adaptively (agent 0 only to avoid redundancy)
        # Interval shrinks if LLM is fast, grows if slow
        if (
            self._llm is not None
            and self._agent_id == 0
            and self._step_index - self._last_llm_step >= self._llm_interval
        ):
            self._last_llm_step = self._step_index
            self._llm_analyze()
            self._adapt_interval()

        return action

    def _llm_analyze(self) -> None:
        """Call Claude to analyze current game state and log insights."""
        try:
            # Build context from current state
            state = self._previous_state
            if state is None:
                return

            inv = state.self_state.inventory
            team = state.team_summary
            resources = {}
            if team:
                resources = {r: int(team.shared_inventory.get(r, 0)) for r in _ELEMENTS}

            lines = [
                f"You are analyzing a CogsVsClips game at step {self._step_index}/10000.",
                f"Agent 0 position: ({state.self_state.position.x}, {state.self_state.position.y})",
                f"HP: {inv.get('hp', 0)}, Hearts: {inv.get('heart', 0)}",
                f"Gear: aligner={inv.get('aligner', 0)} scrambler={inv.get('scrambler', 0)} miner={inv.get('miner', 0)}",
                f"Hub resources: {resources}",
            ]
            if team:
                roles: dict[str, int] = {}
                for m in team.members:
                    roles[m.role] = roles.get(m.role, 0) + 1
                lines.append(f"Team roles: {roles}")

            lines.append(
                "\nIn 2-3 sentences: What is going well? What's the biggest risk? "
                "What one change would improve score most?"
            )

            t0 = time.perf_counter()
            response = self._llm.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=200,
                temperature=0.3,
                messages=[{"role": "user", "content": "\n".join(lines)}],
            )
            latency_ms = (time.perf_counter() - t0) * 1000

            text = ""
            for block in response.content:
                if hasattr(block, "text"):
                    text = block.text
                    break

            self._llm_latencies.append(latency_ms)
            entry = {
                "step": self._step_index,
                "latency_ms": round(latency_ms),
                "interval": self._llm_interval,
                "analysis": text,
                "resources": resources,
            }
            self._llm_log.append(entry)
            print(
                f"[coglet] step={self._step_index} llm={latency_ms:.0f}ms "
                f"interval={self._llm_interval}: {text[:100]}",
                flush=True,
            )

        except Exception as e:
            self._llm_log.append({
                "step": self._step_index,
                "error": str(e),
            })

    def _adapt_interval(self) -> None:
        """Adjust LLM call frequency based on measured latency.

        If LLM is fast (<2s), call more often. If slow (>5s), back off.
        Target: use ~10% of step time budget for LLM calls.
        """
        if not self._llm_latencies:
            return
        avg_ms = sum(self._llm_latencies[-5:]) / min(len(self._llm_latencies), 5)
        if avg_ms < 2000:
            self._llm_interval = max(200, self._llm_interval - 50)
        elif avg_ms > 5000:
            self._llm_interval = min(1000, self._llm_interval + 100)
        # else keep current interval
