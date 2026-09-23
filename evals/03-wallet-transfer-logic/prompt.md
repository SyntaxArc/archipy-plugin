---
max_turns: 30
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit]
runs: 3
scaffold_script: scaffold.sh
---
Add a use case in the `wallet` domain that moves credit from one wallet to another. Both balance updates must succeed or fail together.
