# Test In Progress: 20260404-023

**Status**: Testing seeds 42-46
**Started**: 2026-04-04 UTC (auto-resumed by delta)
**Current**: Seed 44 running

## Change

**Focus**: Hub penalty mid-tier reduction

**File**: `src/cogamer/cvc/agent/scoring.py` - line 71

**Description**: 
Reduced mid-range (15-25 distance) hub_penalty multiplier from 3.0 to 2.7 (-10%) for better accessibility.

## Results

**Baseline (hub_penalty 3.0)**:
- Seed 42: 5.42 per cog

**Attempt 023 (hub_penalty 2.7)**:
- Seed 42: 8.06 per cog (+48.7% vs baseline!)
- Seed 43: 9.76 per cog  
- Seed 44: Running...
- Seed 45: Pending
- Seed 46: Pending

**Average so far**: (8.06 + 9.76) / 2 = 8.91 per cog

**vs Baseline**: 8.91 vs 5.42 = +64.4% improvement

## Monitoring

```bash
tail -30 test_attempt_023_seed_44.txt
```

Each seed takes ~30-35 min on CPU-only.
