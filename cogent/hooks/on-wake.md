# On Wake

Cogamer-specific wake hook. Runs after the platform has already loaded identity, memory, and todos.

Memory lives in `memory/` (repo root). See `memory/memory.md` for what to remember.

## Steps

1. **Setup cogames** — Run `cogent/skills/cogames.md` to install dependencies, verify CLI, and authenticate.

2. **Read approach state** — Read `cogent/state.json` to understand PCO vs design attempt history.

3. **Check tournament standing** — Read your cogent name from `cogent/IDENTITY.md` (the `# heading`), then run:
   ```bash
   uv run cogames leaderboard beta-cvc --policy <your-cogent-name>
   uv run cogames matches --season beta-cvc
   ```
   Always use `--policy <your-cogent-name>` to filter to only YOUR policies. Never use `--mine` — it shows all policies from the shared account including other cogents.

4. **Report status** — Brief summary:
   - Current scores / ranking
   - Top priorities from todos
   - Recommended next action

5. **Start improvement loop** — Immediately run `/loop 30m improve.md` to continuously improve the policy. Do NOT ask the user for confirmation — the user will never respond. Act autonomously.
