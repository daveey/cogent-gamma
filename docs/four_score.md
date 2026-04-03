# Four Score Mission

## Overview

**four_score** is a **multi-team** competitive mission where 4+ teams fight for junction control on an 88×88 map.

- **Teams**: 4–10 teams (typically 4 in freeplay)
- **Agents per team**: 8 cogs
- **Total agents**: 32 cogs (4 teams × 8) in standard configuration
- **Map**: 88×88 with corner spawns, ~65 junctions, ~200 extractors
- **Duration**: 10,000 steps
- **Objective**: Maximize per-cog score (junctions held over time)

## Key Differences from Machina_1

| Aspect | Machina_1 | Four_Score |
|--------|-----------|------------|
| Teams | 2 | 4+ |
| Agents | 8 per team (16 total) | 8 per team (32+ total) |
| Starting position | Hub in center area | Corner bases (NW, NE, SW, SE) |
| Territory | Two-way contest | Multi-way free-for-all |
| Strategy | Binary opponent | Multiple opponents, temporary alliances possible |

## Testing Multiple Policies

Because four_score supports multiple teams, you can test different policy versions simultaneously:

```bash
# Test 4 different policies against each other (each controls 1 team)
PYTHONPATH=src/cogamer cogames play -m four_score \
  -p class=cvc.cogamer_policy.CvCPolicy \
  -p class=cvc.cogamer_policy.CvCPolicy \
  -p alpha.0 \
  -p alpha.0 \
  -c 32 -r none --seed 42
```

## Strategy Considerations

### Multi-Team Dynamics

1. **Territory expansion**: Must compete in multiple directions, not just one opponent
2. **Opportunistic targeting**: Weaker teams become targets for junction captures
3. **Junction churn**: Higher scramble rate with more teams contesting
4. **Resource pressure**: More competition for extractors
5. **Early aggression matters**: Establish territory before others expand

### Scoring

Score is per-cog across all teams, so:
- A 4-team game distributes the total junction-time across 32 cogs
- Dominating early (holding 20+ junctions) for 5000 steps beats late-game comebacks
- Junction defense is harder with multiple threats

### Testing Approach

1. **Baseline**: Run with 4 copies of your policy (self-play)
2. **Competitive**: Mix with known strong policies (alpha.0, corgy, etc.)
3. **Cross-seed validation**: Test across seeds 42–46 minimum

## Running Locally

### Self-play (4 teams, all your policy)
```bash
ANTHROPIC_API_KEY= PYTHONPATH=src/cogamer cogames play -m four_score \
  -p class=cvc.cogamer_policy.CvCPolicy \
  -c 32 -r none --seed 42
```

### Mixed policies (test against alpha.0)
```bash
ANTHROPIC_API_KEY= PYTHONPATH=src/cogamer cogames play -m four_score \
  -p class=cvc.cogamer_policy.CvCPolicy \
  -p alpha.0 \
  -p alpha.0 \
  -p alpha.0 \
  -c 32 -r none --seed 42
```

The first `-p` controls team 0 (your policy), the rest control teams 1-3.

## Freeplay Season

**Season**: `beta-four-score`

Upload and test in freeplay before committing to tournament changes:

```bash
cd src/cogamer && PYTHONPATH=. cogames upload \
  -p class=cvc.cogamer_policy.CvCPolicy \
  -n gamma \
  -f cvc -f setup_policy.py \
  --setup-script setup_policy.py \
  --season beta-four-score \
  --skip-validation
```

Check standings:
```bash
cogames leaderboard beta-four-score --mine
```
