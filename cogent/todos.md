# gamma — Improvement TODOs

## Completed
- [x] (ID) Wider enemy AOE for retreat: wired _near_enemy_territory (radius 20) into _should_retreat — +458% avg score
- [x] (20260403) LLM objective feature: wired up expand/defend/economy_bootstrap objectives to pressure budgets — was broken, now functional
- [x] (20260403) Documentation: added four_score.md, updated all docs for multi-team format

## Candidates
- [ ] Hotspot tracking: already tracked in _hotspots dict, used in scoring — verify it's working correctly in four_score
- [ ] LLM stagnation detection: detect stuck agents and adjust directives (analyze program can set role override)
- [ ] Read teammate vibes for coordination
- [ ] Four_score specific tuning: corner spawns, multi-directional expansion, higher junction churn
- [ ] Test mixed-policy matches (vs alpha.0, corgy) to validate competitive performance
