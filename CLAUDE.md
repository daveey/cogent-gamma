# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Related Repos

- **metta-ai/cogos** — CogOS operating system
- **metta-ai/cogora** — Cogora platform

## Project Structure

```
src/coglet/     # Framework: Coglet base class + mixins
cogames/        # CvC player: Coach, PlayerCoglet, PolicyCoglet
docs/           # Architecture design docs
```

## Architecture

Coglet is a framework for fractal asynchronous control of distributed agent systems, built on two primitives:

- **COG** (Create, Observe, Guide) — slow, reflective supervisor that spawns and manages LETs
- **LET** (Listen, Enact, Transmit) — fast, reactive executor that handles events

A Coglet is both: every COG is itself a LET under a higher COG, forming a recursive temporal hierarchy. The COG/LET boundary is a protocol contract, not a deployment boundary.

### Communication Model

- **Data plane**: `@listen(channel)` — receive data from named channels
- **Control plane**: `@enact(command_type)` — receive commands from supervising COG
- **Output**: `transmit(channel, data)` — push results outbound
- **Supervision**: `observe(handle, channel)`, `guide(handle, command)`, `create(config)`
- All communication is async, location-agnostic, fire-and-forget

### Mixins

LifeLet (lifecycle hooks), GitLet (repo-as-policy), LogLet (log stream), TickLet (`@every` periodic), CodeLet (mutable function table), MulLet (fan-out N children).

### CvC Player Stack

Coach (Claude Code) → PlayerCoglet (GitLet) → PolicyCoglet (CodeLet + LLM brain)

### Key Commands

```bash
# Play locally
cogames play -m machina_1 -p class=cvc.cvc_policy.CogletPolicy -c 8 --seed 42

# Upload to tournament
cogames upload -p class=cvc.cvc_policy.CogletPolicy -n coglet-v0 \
  -f cvc -f mettagrid_sdk -f setup_policy.py \
  --setup-script setup_policy.py --season beta-cvc
```

### Docs

- [README.md](README.md) — Project overview and quickstart
- [docs/coglet.md](docs/coglet.md) — Architecture design (COG/LET primitives)
- [docs/framework.md](docs/framework.md) — Framework implementation reference
- [docs/tournament.md](docs/tournament.md) — Tournament system design
- [docs/cvc-player.md](docs/cvc-player.md) — CvC player system (Coach, Player, Policy)
