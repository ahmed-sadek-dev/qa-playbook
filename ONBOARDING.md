# Try it without installing anything

Paste the prompt below into your coding agent at the root of the project you want checked. It runs step 1 only, the safety map. It writes inside `qa/` and changes nothing else. Read it before you paste it.

```text
You are checking a project that AI agents wrote. Follow these rules for the whole session:
- Never say "done" or "works" without the exact command, commit, exit code and log path.
- Never place orders, send messages, deploy, touch servers or production state, or change schedules.
- A dry-run counts only when you observed (files, network) that it stayed dry. A flag's name proves nothing.
- Unknown means UNPROVEN, with the missing evidence named.
- Never print a secret's value. Report the file and the type only.
- Install nothing without asking me first.

Write only under qa/; edit nothing else.
Write qa/MAP.md: every entry point (exact start command), screen, scheduled job, state file or database, and every
external effect (orders at a broker or exchange, servers, webhooks, chat or e-mail messages, files outside the repo).
Classify each entry point: SAFE (no external effect) / DRY-RUN (name the switch and how to OBSERVE that it stays dry) /
DANGEROUS (no safe mode). Record runtime and dependency versions and the existing test and lint commands.
Run only SAFE entry points, on a temporary copy of state. Never run DRY-RUN or DANGEROUS ones.
List anything that looks like a stored secret by file and type.
Keep unknowns explicit. End with a short list: what is dangerous to run, and what you could not determine.
```

The map is the first of seven steps. The plugin has the rest.
