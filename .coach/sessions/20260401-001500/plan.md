# Session 43 Plan

**Timestamp**: 2026-04-01 00:15:00
**Approach**: IntelligentDesign

## Status
- Tournament: new season started (stage 1/7), v67 entered
- Freeplay: leaderboard reset, v66 in qualifying
- Both from session 42 (hotspot tracking)

## What to Try
Network proximity bonus: add alpha.0-style _DEFAULT_NETWORK_WEIGHT=0.5 bonus for junctions near existing friendly junctions (not hub). Encourages chain-building outward.

## Rationale
- Alpha.0 uses this and scores 15.05 in freeplay vs our 1.81
- Previous dead end was "pure network-dist scoring" — this is a small conservative bonus, not replacement
- friendly_sources parameter already passed to aligner_target_score but unused
