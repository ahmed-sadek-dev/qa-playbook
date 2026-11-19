# qa-playbook

A Claude Code plugin that certifies a project written by AI agents.

Every promise in the project ends in one of three states: VERIFIED by a command that ran on a known commit, BROKEN with a failing test, or UNPROVEN with the missing evidence named. Nothing is assumed silently.

Author: Ahmed Sadek (github.com/ahmed-sadek-dev). Version 0.1.0, 19 November 2026.

## Why

AI agents write code that passes its own tests. Those tests are often written from the code's own output, so a green run proves little. This routine has the owner state the expected numbers first, and it ties every "works" to a command and a commit.

## What is in it

- The skill `certify`: seven steps, from a safety map to a report.
- 26 bug classes found while certifying two AI-built trading apps, each with the check that catches it.
- A stability check for LLM decision systems, with a script that counts how often the same input gives the same decision.

## The seven steps

1. Safety map: what exists, and what must not be run.
2. Contract: numbered promises, with expected values from the owner.
3. Gate: one command for all checks, proven to fail when the code breaks.
4. Logic: the important promises tested against the owner's numbers.
5. End to end: the real program, in safe modes only.
6. Screen: the numbers shown equal the numbers verified.
7. Independent review, fixes and report.

## Install

In Claude Code:

```
/plugin marketplace add ahmed-sadek-dev/qa-playbook
/plugin install qa-playbook@qa-playbook
```

Then run `/qa-playbook:certify` in the project you want checked.

To try the first step without installing anything, use the prompt in `ONBOARDING.md`.

## The stability script

```
python skills/certify/scripts/stability.py runs.jsonl
python skills/certify/scripts/stability.py --selftest
```

Python 3.10 or later, no packages. On the author's own LLM trading desk, the same input gave the same picks in 8 of 10 cases.

## Where it comes from

The routine was written for nine AI-built trading projects in October 2026. The bug classes come from the first two projects that went through it.

## Limits

- It does not prove that a project has no bugs.
- It checks that the code does what was promised. It does not judge whether a trading strategy makes money.
- Step 2 needs the owner's time. The author's estimate is 1 to 3 hours per project, and that estimate was not measured.
- The plugin never places orders and never asks you to loosen permissions.

## How this was made

The method came out of a review between two AI coding agents and the author. The text was produced with an AI coding agent under the author's direction.

## License

MIT. See `LICENSE`.
