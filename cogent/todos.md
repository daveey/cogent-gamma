# scissors — Improvement TODOs

## Candidates
- [x] Hotspot tracking: track scramble events per junction, deprioritize frequently-scrambled junctions (already implemented in junctions.py, scoring.py)
- [x] (ID) Wider enemy AOE for retreat: wired _near_enemy_territory (radius 20) into _should_retreat — +458% avg score
- [x] RETREAT_MARGIN 15→20: tested, regressed (-13%), reverted (too conservative with our existing enemy detection)
- [ ] LLM stagnation detection: detect stuck agents and adjust directives
- [ ] Read teammate vibes for coordination
