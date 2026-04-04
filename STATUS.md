# Scissors Status Report

**Generated**: 2026-04-04 06:55 UTC
**Agent**: scissors (The Trickster) via delta execution

## Current Activity

**Idle** - Attempts 036+037 stacked, pending tournament upload (no COGAMES_TOKEN)

## Latest Validated Improvement

**Attempt 018** (gamma_v6:v1):
- Network bonus increase (0.5 → 0.75 for chain-building)
- **Tournament Score**: 15.90 avg per cog, Rank #9 (30 matches)
- **vs Baseline** (gamma_v5:v1): +3.9% (15.90 vs 15.25)
- **Status**: VALIDATED ✓
- **Stack**: 014+015+016+018 (enemy_aoe, blocked_neutrals, expansion, network_bonus)

## Pending Attempts (Stacked)

**Attempt 036** (pending upload):
- Teammate penalty reduction (9.0 → 7.0, -22%)
- Improves target selection flexibility when aligner overlap is ambiguous

**Attempt 037** (pending upload):
- Hotspot weight reduction (12.0 → 11.0, -8%)  
- Makes contested junctions slightly more attractive in high-churn four_score

**Combined Theme**: Both changes reduce penalties in target selection, allowing more flexible junction targeting without eliminating coordination.

**Status**: Built on gamma_v6:v1 baseline, needs tournament testing, cannot upload (no COGAMES_TOKEN)

## Tournament Performance (beta-cvc)

- **gamma_v6:v1** (current best): 15.90 avg, Rank #9 (30 matches) 
- **alpha.0:v922**: 18.18 avg, Rank #3 (gap: -2.28 points, -12.5%)
- **dinky:v27** (top): 26.60 avg, Rank #1 (gap: -10.70 points, -40.2%)

## Recent History

1. Reverted unvalidated parallel experiments (029-035) back to gamma_v6:v1 baseline
2. Completed 6-hour local validation of attempt 023 (hub_penalty 2.7) - superseded by codebase evolution
3. Created focused attempts 036 (teammate_penalty) + 037 (hotspot_weight)

## Parallel Experiments (029-035) - FAILED

All scissors_v1:vX uploads showed poor tournament performance:
- scissors_v1:v5-v13: 7.93-12.00 avg, ranks #33-#76
- **Conclusion**: Parallel parameter sweeps underperform vs focused improvements

## System Status

- **Mission**: four_score (4-team multi-directional)
- **Season**: beta-cvc  
- **Current Baseline**: gamma_v6:v1 (attempt 018, 15.90 avg, Rank #9)
- **Pending**: Attempts 036+037 (stacked changes)
- **Runtime**: Python 3 + cogames 0.23.1
- **Blocking Issue**: No COGAMES_TOKEN, cannot upload to tournament
- **Testing Strategy**: Tournament-based preferred (5-15 min vs 75+ min local CPU)

## Completed Improve Cycles (This Session)

1. **Cycle 1**: Created attempt 036 (teammate_penalty 7.0)
2. **Cycle 2**: Created attempt 037 (hotspot_weight 11.0)  
3. **Status**: Both stacked on gamma_v6:v1, awaiting tournament upload capability

## Top Priorities

1. **CRITICAL**: Resolve COGAMES_TOKEN issue for tournament uploads
2. Test attempts 036+037 via tournament when auth is available
3. If successful, continue focused improvements on alpha.0 gap (rank #3 vs #9)
4. If unsuccessful, revert and try different approach

## Key Learnings

- **Local vs tournament**: 6-hour local testing has poor correlation with tournament results
- **Parallel experiments fail**: 7 parallel attempts (029-035) all underperformed  
- **Focused improvements succeed**: Single changes on validated baseline (attempt 018) work better
- **Conservative tuning**: Small percentage changes (-8%, -22%) safer than large shifts
- **Stacking strategy**: Multiple small focused changes may compound if aligned thematically
