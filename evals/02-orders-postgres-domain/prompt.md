---
max_turns: 40
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit]
runs: 3
scaffold_script: scaffold.sh
---
We need to store customer orders in Postgres and expose them over HTTP. Set up the `order` domain end to end in this ArchiPy app.
