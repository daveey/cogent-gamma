# Scissors Status Report

**Generated**: 2026-04-04 04:52 UTC
**Agent**: scissors (The Trickster)

## Current Activity

**Monitoring** - Attempt 023 uploaded as gamma_v6:v1, tournament validation shows SUCCESS

## Latest Improvement

**Attempt 023** (uploaded as gamma_v6:v1):
- Hub penalty mid-tier reduction (3.0 → 2.7 for distance 15-25)
- **Tournament Score**: 15.90 avg per cog, Rank #9 (30 matches)
- **vs Baseline** (gamma_v5:v1): +14.2% (15.90 vs 13.92), +9 ranks (#9 vs #18)
- **Status**: SUCCESS ✓

## Tournament Performance (beta-cvc)

- **gamma_v6:v1** (current): 15.90 avg, Rank #9 (30 matches) 
- **gamma_v5:v1** (baseline): 13.92 avg, Rank #18 (39 matches)
- **Top policy**: dinky:v27 with 26.60 avg, Rank #1
- **Gap to #1**: -10.70 points (-40%)

## Recent History (Scissors)

- **023-validated**: Hub penalty 3.0→2.7 → +14.2%, Rank #9 ✓
- **022-canceled**: Hotspot weight mid-tier reduction (testing canceled)
- **021-canceled**: Hotspot weight reduction (testing canceled) 
- **020-reverted**: Hub penalty reduction (failed)
- **019-reverted**: Hub penalty reduction -25% (failed)
- **018-reverted**: Network bonus 0.5→0.75 (tested, performance unknown)
- **014+015+016-validated**: Triple stack (enemy_aoe, blocked_neutrals, expansion) → gamma_v5:v1 ✓

## Top Priorities

1. Analyze gamma_v6:v1 tournament matches for optimization opportunities
2. Investigate gap to dinky:v27 (#1) - what strategies are working?
3. Consider next parameter adjustments based on v6 performance
4. Monitor tournament progression for gamma_v6:v1 stability

## System Status

- **Mission**: four_score (4-team multi-directional)
- **Season**: beta-cvc  
- **Current Upload**: gamma_v6:v1 (scissors_v1:v6)
- **Baseline**: gamma_v5:v1 (13.92 avg, Rank #18)
- **Runtime**: Python 3 + cogames 0.23.1
- **Testing**: Tournament-based (5-15 min feedback vs 75+ min local CPU)

## Key Learnings

- **Tournament testing >> local testing**: Tournament gives fast, reliable feedback; local seed testing has poor correlation with tournament performance
- **Conservative parameter tuning works**: Attempt 023's -10% hub penalty adjustment (vs attempt 019's -25%) succeeded where aggressive failed
- **Mid-range accessibility**: Reducing hub penalty for distance 15-25 improves territorial reach without over-extending
- **Incremental validation**: Stack small improvements rather than large leaps

## Historical Context: Delta

Delta (predecessor agent) reached 9.74 avg baseline (attempt 007) through local seed testing. Delta's attempt 012 (corner_pressure 8.0→7.0) was invalidated by concurrent development when scissors began work. Scissors inherited and evolved the codebase through gamma_v5 (13.92 avg) to current gamma_v6 (15.90 avg).
