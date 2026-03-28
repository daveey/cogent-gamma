"""Coach: orchestrates PlayerCoglet across many games.

The Coach is NOT a Coglet — it's a Claude Code session that:
1. Submits PolicyCoglet to cogames for each game
2. Reads learnings/experience after each game
3. Analyzes across games
4. Commits improvements to the repo
5. Repeats
"""
from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path
from typing import Any

_LEARNINGS_DIR = os.environ.get("COGLET_LEARNINGS_DIR", "/tmp/coglet_learnings")


def play_game(
    mission: str = "machina_1",
    seed: int = 42,
    render_mode: str = "none",
    num_cogs: int = 8,
) -> dict[str, Any]:
    """Run a single game locally and return results + learnings."""
    cmd = [
        "cogames", "play",
        "-m", mission,
        "-p", "class=cvc.cvc_policy.CogletPolicy",
        "-c", str(num_cogs),
        "-r", render_mode,
        "--seed", str(seed),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    return {
        "stdout": result.stdout,
        "stderr": result.stderr,
        "returncode": result.returncode,
        "learnings": read_latest_learnings(),
    }


def upload_policy(
    name: str = "coglet-v0",
    season: str = "beta-cvc",
) -> str:
    """Upload the current policy to cogames tournament."""
    cmd = [
        "cogames", "upload",
        "-p", "class=cvc.cvc_policy.CogletPolicy",
        "-n", name,
        "-f", "cvc",
        "-f", "mettagrid_sdk",
        "-f", "setup_policy.py",
        "--setup-script", "setup_policy.py",
        "--season", season,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    return result.stdout + result.stderr


def read_latest_learnings() -> dict[str, Any] | None:
    """Read the most recent game's learnings."""
    learnings_dir = Path(_LEARNINGS_DIR)
    if not learnings_dir.exists():
        return None
    files = sorted(learnings_dir.glob("game_*.json"), key=lambda p: p.stat().st_mtime)
    if not files:
        return None
    return json.loads(files[-1].read_text())


def read_all_learnings() -> list[dict[str, Any]]:
    """Read all accumulated game learnings."""
    learnings_dir = Path(_LEARNINGS_DIR)
    if not learnings_dir.exists():
        return []
    results = []
    for path in sorted(learnings_dir.glob("game_*.json")):
        results.append(json.loads(path.read_text()))
    return results


def summarize_experience(learnings: list[dict[str, Any]]) -> str:
    """Summarize learnings across games for analysis."""
    if not learnings:
        return "No games played yet."
    lines = [f"Experience from {len(learnings)} games:\n"]
    for game in learnings:
        gid = game.get("game_id", "?")
        duration = game.get("duration_s", 0)
        llm_log = game.get("llm_log", [])
        n_calls = len(llm_log)
        analyses = [e.get("analysis", "") for e in llm_log if "analysis" in e]
        latencies = [e.get("latency_ms", 0) for e in llm_log if "latency_ms" in e]
        avg_lat = sum(latencies) / len(latencies) if latencies else 0

        lines.append(f"Game {gid} ({duration}s, {n_calls} LLM calls, avg {avg_lat:.0f}ms):")
        for a in analyses[-3:]:  # last 3 analyses
            lines.append(f"  - {a[:150]}")
        lines.append("")
    return "\n".join(lines)
