---
name: certify
description: Certify an AI-built project in seven steps. Use when asked to QA, verify, audit or sign off a codebase that AI agents wrote, to prove or disprove "it works", to map what is unsafe to run, to write a contract of promises, to build a test gate, or to check whether an LLM decision system gives the same answer twice. Every promise ends VERIFIED, BROKEN or UNPROVEN with evidence.
---

# Certify an AI-built project

No tool proves that a project has no bugs. What can be complete is this: every promise in the project's contract is VERIFIED by a command that ran on a known commit, BROKEN with a failing test, or UNPROVEN with the missing evidence named. Nothing is assumed silently.

Each project gets three files in `qa/`:

- `MAP.md`: what is in the project and where the risk is.
- `CONTRACT.md`: the promises, meaning what the project is supposed to do.
- `REPORT.md`: the status of each promise and its evidence.

## Rules

Paste this block into the project's agent instruction file (CLAUDE.md, AGENTS.md) and follow it yourself:

```text
## QA rules (do not remove)
R1 Evidence: never say "done" or "works" without the exact command, commit, exit code, test counts and log path.
R2 Isolation: during QA, never place orders, send messages, deploy, touch servers or production state, or change schedules.
   A dry-run counts only when observation (files, network) proves it stayed dry; a flag's name proves nothing.
R3 Tests: never delete, weaken or skip a check to get green. Report test edits separately from code edits.
R4 Bugs: every fix starts with a reproducer that fails for the reported reason; one bounded change per bug.
R5 Contract: the owner owns intended behaviour. Code-derived behaviour is "observed", never "correct".
   Do not fill expected values from the code's own output.
R6 Two failed attempts on the same hypothesis -> stop and re-diagnose; no third patch of the same idea.
R7 Unknown = UNPROVEN, naming the missing evidence. Any change invalidates the evidence it touches; rerun those checks.
```

## Safety

- Write only under `qa/`, `tests/contract/` and `scripts/gate.*`. Change app code only with the fix prompt.
- Never print a secret's value. Report the file and the type.
- Ask the owner before installing a tool, and before any run that costs money or many tokens.

## Steps

Read `references/steps.md` for the prompt of the step you are on. One step per session works best.

1. **Safety map.** Every entry point is SAFE, DRY-RUN or DANGEROUS.
2. **Contract.** Numbered promises. The owner supplies the expected values for the important ones. This is the only step that needs the owner's judgment.
3. **Gate.** One command runs all checks and is proven to fail when the code breaks.
4. **Logic.** Each important promise is tested against the owner's number, never against the code's own output. Check every class in `references/bug-classes.md`.
5. **End to end.** The real program runs the way a user runs it, in safe modes only.
6. **Screen.** Every number shown equals the verified number, and every button does what the contract says.
7. **Independent review, fixes, report.**

If an LLM picks, rates or decides anything in the project, also read `references/llm-stability.md`.

## Order and fixing

- Several projects: pilot the full routine on the cheapest one. Then run steps 1 and 3 on all of them, since they are mechanical. Then steps 2, 4, 5, 6 and 7 project by project, highest real risk first.
- Fix at the end of a step, never in the middle, with the fix prompt in `references/steps.md`. Fix first what later steps depend on.
- After any change, rerun the gate and the checks the change touches. Old evidence belongs to the commit it ran on.
- Short on time, cut in this order: step 6 on screens that show no money, mutation testing, the second model in step 7. Never cut the safety map, the gate or the logic of the important promises.
