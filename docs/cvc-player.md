# CvC Player System

The CvC (Cogs vs Clips) player is a three-layer stack built on the Coglet framework.

## Stack Overview

```
Coach (Claude Code session)
  └── PlayerCoglet (GitLet COG — cross-game management)
        └── PolicyCoglet (CodeLet — per-game LLM brain + Python heuristic)
              └── CogletBrainAgentPolicy (per-agent: heuristic + LLM analysis)
```

## Coach (`cogames/coach.py`)

The Coach is **not a Coglet** — it's a Claude Code session that:

1. Runs games via `cogames play` CLI
2. Reads learnings/experience written by PolicyCoglet
3. Maintains a changelog (`cogames/coach_log.jsonl`)
4. Analyzes performance across games
5. Commits code improvements to the repo
6. Uploads improved policy to tournament

### Changelog

One JSON object per line in `coach_log.jsonl`. Three entry types:

| Type | Fields | Purpose |
|---|---|---|
| `game` | game_id, score, llm_calls, duration_s | Record completed game |
| `insight` | insight, source | Analysis observation |
| `change` | description, files | Code modification |

### API

```python
from cogames.coach import play_game, upload_policy, summarize_experience

# Run a local game
result = play_game(mission="machina_1", seed=42, num_cogs=8)
# result["score"], result["learnings"], result["stdout"]

# Upload to tournament
upload_policy(name="coglet-v0", season="beta-cvc")

# Review all experience
print(summarize_experience())
```

## PlayerCoglet (`cogames/player.py`)

A Coglet with GitLet + LifeLet mixins that manages PolicyCoglets across multiple games.

```python
class PlayerCoglet(Coglet, GitLet, LifeLet):
    @listen("game_complete")
    async def handle_game_complete(self, data):
        # Reads learnings from PolicyCoglet's output files
        # Accumulates experience across games

    @enact("improve")
    async def handle_improve(self, analysis):
        # Coach directs improvements via this command
```

## PolicyCoglet (`cogames/cvc/cvc_policy.py`)

The main policy submitted to cogames. Implements `MultiAgentPolicy` (cogames interface).

### Two speeds

1. **Python heuristic** (`CogletAgentPolicy`) — handles every step, fast path
2. **LLM brain** (Claude via Anthropic API) — analyzes ~14 times per 10K-step episode

### CogletPolicy (MultiAgentPolicy)

```python
class CogletPolicy(CogletBasePolicy):
    short_names = ["coglet", "coglet-policy"]
    minimum_action_timeout_ms = 30_000

    # Creates CogletBrainAgentPolicy per agent
    # On reset() (end of episode): writes learnings to disk
```

### CogletBrainAgentPolicy (per-agent)

```python
class CogletBrainAgentPolicy(CogletAgentPolicy):
    # Inherits full heuristic from CogletAgentPolicy
    # Every _LLM_INTERVAL steps (agent 0 only):
    #   1. Builds game state context
    #   2. Calls Claude for analysis
    #   3. Logs to _llm_log
    #   4. Adapts interval based on latency
```

Adaptive interval:
- Starts at 500 steps
- If LLM latency < 2s: shrink interval (more frequent calls)
- If LLM latency > 5s: grow interval (less frequent calls)
- Range: 200–1000 steps

### Heuristic Stack

```
CogletBrainAgentPolicy        (LLM brain overlay)
  └── CogletAgentPolicy        (optimized heuristic)
        └── SemanticCogAgentPolicy  (base semantic policy from cogora)
```

`CogletAgentPolicy` extends the base with:
- Resource-aware macro directives (mine least-available resource)
- Phase-based pressure budgets (aligner/scrambler allocation over time)
- Miner safety retreat logic

`SemanticCogAgentPolicy` (~1300 lines) handles:
- Role assignment (miner, builder, defender)
- Pathfinding with corridor navigation
- Resource gathering and junction alignment
- Team coordination via shared world model

## Learnings Flow

```
PolicyCoglet (in-game)
  └── Writes to /tmp/coglet_learnings/game_*.json
        ├── game_id, duration_s
        ├── summary (per-agent stats)
        └── llm_log (all LLM analyses with step, latency, resources)

Coach (post-game)
  └── Reads learnings, logs to coach_log.jsonl
        ├── Analyzes patterns across games
        ├── Identifies improvements
        └── Commits code changes
```

## Tournament

Upload bundles `cvc/` + `mettagrid_sdk/` + `setup_policy.py` as a ZIP. The setup script installs the `anthropic` SDK in the tournament sandbox. Season: `beta-cvc`.

```bash
cogames upload -p class=cvc.cvc_policy.CogletPolicy -n coglet-v0 \
  -f cvc -f mettagrid_sdk -f setup_policy.py \
  --setup-script setup_policy.py --season beta-cvc
```
