# LLM output stability

Read this when an LLM picks, rates or decides anything in the project.

Code gives the same output for the same input. An LLM may not. Before anyone credits a changed decision to a new input, measure how often the decision changes when nothing changed.

## Rule first

Write the pass or fail rule in `qa/` before the first run. A default that has been used in practice:

- stable: the same decision in at least 8 of 10 cases
- unstable: the same decision in 5 or fewer of 10 cases
- anything between is inconclusive

## Method

1. Pick at least 10 past decision cases. Freeze each one's full input in a file.
2. State the cost before running. Each run is a full LLM call. Use a read-only agent with no tools beyond reading the file, which keeps runs comparable and cheap.
3. Run every case twice, in fresh sessions, on the identical file. Give runs random ids so whoever records the decisions cannot tell which runs belong together.
4. Save one line per run in `qa/evidence/runs.jsonl`: `{"case": "c01", "run": 1, "decision": ["BTC", "ETH"]}`.
5. Count with the script in this skill's folder: `python <skill folder>/scripts/stability.py qa/evidence/runs.jsonl`. Run it with `--help` for the thresholds.
6. Record the contract row as VERIFIED (stable), BROKEN (unstable) or UNPROVEN (inconclusive). Change no code and no prompt in this step.

## A stronger follow-up: the fake-signal test

Stability shows the system repeats itself. It does not show that it weighs its inputs. Run four arms per case on the same frozen input, each in a fresh session with a blinded run id:

- C1 and C2: no signal. Two identical runs; they also give the stability measure.
- T: one signal line naming a market that rose afterwards.
- F: the same line naming a market that fell afterwards.

The named market is one the rules allow buying and the system does not hold. Never show the case's original decision.

Count, out of 10 cases: followed(T) and followed(F), the runs that buy the named market; and baseline, how often C1 and C2 buy that same market (their average). Write this rule before the runs:

- tells right from wrong: followed(T) − followed(F) ≥ 5
- moved by a wrong signal: followed(F) − baseline(F) ≥ 5
- ignores signals: followed(T) − baseline(T) ≤ 2 and followed(F) − baseline(F) ≤ 2
- anything else: inconclusive

Cost: four full runs per case. Measure one unscored format-check run first and state the total before starting. A run without a readable decision is rerun once with the same input, then counts as "buys nothing".
