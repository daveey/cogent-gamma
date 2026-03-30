# Session Log: 20260330-103000

## 2026-03-30 10:30 — Session started
Focus: investigate seed variance, improve economy

## Previous Session Results (v17)
- v17 still qualifying (not yet on leaderboard)
- v16 settled: 1.91 (24 matches)
- v14 improved: 3.96 (422 matches) — our tournament best
- Top: alpha.0:v547 at 14.69

## Experiment A: Resource-aware pressure budgets (use parent PressureMixin)
- Hypothesis: static budgets starve aligners when economy is weak
- Removed CogletAgentPolicy._pressure_budgets override
- Result: avg 3.25 (seeds 42=2.68, 43=5.93, 44=1.72, 45=1.76, 46=4.16) — REGRESSION from 6.18
- Parent version too aggressively scales back aligners. Reverted.

## Experiment B: Chain-aware junction scoring ✅
- Root cause: aligner_target_score used hub_penalty based on hub distance only
- Junctions far from hub but near captured junctions got penalty 130+
- This prevented chain-building — agents clustered near hub instead of expanding
- Fix: compute network_penalty from nearest friendly source (hub OR captured junction)
- A junction 5 from a captured junction now gets low penalty regardless of hub distance

### Results
| Seed | v17 Baseline | Chain Scoring | Change |
|------|-------------|---------------|--------|
| 42   | 2.16        | 3.72          | +72%   |
| 43   | 21.59       | 22.90         | +6%    |
| 44   | 1.75        | 11.73         | +570%  |
| 45   | 3.78        | 2.83          | -25%   |
| 46   | 1.63        | 2.50          | +53%   |
| **Avg** | **6.18** | **8.74**      | **+41%** |

## Actions
- Committed: `4f5ec5a` feat: chain-aware junction scoring enables network expansion
- Pushed to main
- Submitted as coglet-v0:v18

## Status: WAITING
Submitted v18, checking tournament results next session.
