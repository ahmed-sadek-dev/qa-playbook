# The seven steps

Each step has a goal, a "done when" and a prompt. P0 means anything that moves money, sends, deletes, or produces a number a user acts on: orders, signals, indicators, sizing, profit and loss. Where a prompt names a kind of skill, use one if it is installed; otherwise do the work directly.

## 1. Safety map

- Goal: know every entry point, screen, scheduled job, state file and external effect, and know what must not run.
- Done when: every entry point is SAFE, DRY-RUN or DANGEROUS, and every unknown is written down.

```text
Write only under qa/; edit nothing else.
Write qa/MAP.md: every entry point (exact start command), screen, scheduled job, state file or database, and every
external effect (orders at a broker or exchange, servers, webhooks, chat or e-mail messages, files outside the repo).
Classify each entry point: SAFE (no external effect) / DRY-RUN (name the switch and how to OBSERVE that it stays dry) /
DANGEROUS (no safe mode). Record runtime and dependency versions and the existing test and lint commands.
Run only SAFE entry points, on a temporary copy of state. Never run DRY-RUN or DANGEROUS ones in this step.
Scan for secrets (for example: detect-secrets scan --all-files, excluding .venv, node_modules and .git) and list real
findings in MAP.md by file and type only, never the value.
Unknowns stay explicit. Finally print the QA rules block for the owner to paste into the agent instruction file.
```

## 2. Contract

- Goal: numbered promises. For the important ones the owner writes the expected number without seeing what the code outputs. Approving a written text is not enough.
- Done when: every capability has a promise or a written exception, and every P0 promise has an expected value from the owner or from an independent reference.
- Then: `git add qa; git commit -m "qa: contract"`, after the owner has filled in the numbers.

```text
List every capability of this project from qa/MAP.md and the code, labelled OBSERVED.
Write qa/CONTRACT.md: one row per capability: ID, risk (P0, P1, P2), Given/When/Then, verification method, source,
status UNPROVEN.
For the 10 to 15 most important P0 rows give a concrete input (data, prices, position, settings) and leave the
"Expected" column EMPTY. Do not run the code to fill it and do not derive it from the code.
The owner fills expected values, or takes them from an independent reference. Rows the owner does not confirm stay UNSURE.
List genuine ambiguities in one "Owner decisions" list. Change no code.
```

## 3. A gate you can trust

- Goal: one command runs every check, and it is proven to fail when the code breaks.
- Done when: the gate prints test counts, fails when zero tests are collected, and goes red on 3 mutations. Failures that existed before are recorded by test name in `qa/BASELINE.md`. The gate may stay red because of old bugs. What matters is that its result can be trusted.
- A project with no tests: record "NO GATE YET". It is not a failure. Build the gate when step 4 adds the first tests.

```text
Create scripts/gate.ps1 (or gate.sh): one command that runs, in order: the linter, the type checker on the P0 files
from qa/CONTRACT.md, ALL tests by auto-discovery, plus any script-style tests listed in qa/MAP.md.
Print collected/passed/failed/skipped counts. Fail when zero tests are collected and on any failure; propagate every
exit code.
Then prove the gate can fail: in 3 P0 functions, temporarily return a constant or empty the body, run the gate, confirm
red, restore, confirm the original result. Report mutations that survived.
Record existing failures by test name in qa/BASELINE.md; do not fix them now. Change no app code.
```

## 4. Prove the logic

- Goal: every P0 promise is tested against the owner's number, not the number the code produced.
- Done when: every P0 row is VERIFIED, BROKEN with the name of the failing test, or UNPROVEN with what is missing.

```text
For every P0 row in qa/CONTRACT.md that has an owner-supplied expected value, write a test in tests/contract/ that
feeds the stated input through the real function and asserts the owner's value within the stated tolerance.
Never change an expected value to match the code.
Check these bug classes on every P0 path and add a test where one applies: lookahead (finished versus still-forming
data), time zones and session boundaries, fees and slippage, float rounding of money, invariants (cash never negative,
size within caps, a rerun is idempotent), plus every class in references/bug-classes.md.
Before comparing with an outside reference, align provider, timeframe, close time, adjustments, fees, rounding and
timestamps. Mark each row VERIFIED / BROKEN (failing test name) / UNPROVEN (what is missing).
Do not fix code in this step.
```

## 5. Prove it runs end to end

- Goal: a project-specific check that drives the real program the way a user does, and that can be repeated after any change.
- Done when: every FLOW row is VERIFIED, BROKEN or UNPROVEN, with its evidence saved in `qa/evidence/`.

```text
Write a verification script or skill for this project.
Scope: the FLOW and SCREEN rows of qa/CONTRACT.md and the entry points in qa/MAP.md.
Drive only SAFE entry points and DRY-RUN modes, on temporary state. Prove a dry-run stayed dry by watching files and
network; never place orders, send messages, or touch servers or production state.
Per flow cover: happy path, rerun (idempotent), restart mid-run, missing data, dependency failure, and scheduling logic
(separately from the real scheduler). Assert persisted results, not just "no crash".
Label evidence simulated / local / deployed. Then run the check and mark each FLOW row VERIFIED / BROKEN / UNPROVEN
with evidence in qa/evidence/. Do not fix code in this step.
```

## 6. Prove the screen

- Goal: every number on screen equals the number verified in step 4, and every button changes state the way the contract says.
- Done when: every SCREEN row has a screenshot and an assertion result.

```text
Run the project's verification check for every SCREEN row in qa/CONTRACT.md; add missing screens to its feature map.
Per screen: every displayed number must equal the independently verified value from step 4 (units, rounding, time zone,
selected account, freshness); every button or action must change state exactly as the contract says; check loading,
empty, error and stale states; no console errors; no clipped text.
Save a screenshot plus the assertion result per row in qa/evidence/. Mark rows VERIFIED / BROKEN / UNPROVEN.
Say whether the source build or the packaged app was tested. Do not fix code in this step.
```

## 7. Independent review, fixes, report

- Goal: a second model reads the whole project against the contract and names behaviour that no promise covers. Every fix is reviewed for what else it touches. Repeated mistakes become a check that stops them coming back. Then the report.
- Done when: `REPORT.md` says "assessment complete". It says "ready for <scope>" only if no P0 row is BROKEN or UNPROVEN.
- Then: run the gate, run the verification check, `git add qa; git commit -m "qa: report"`.

```text
(a) Have a second model, or a fresh session that did not write the code, review this project with qa/CONTRACT.md as the
    acceptance list. Ask it: 1) which contract rows the code contradicts; 2) what behaviour exists that no contract row
    covers. Each finding names its contract row and a reproducer, or is labelled unconfirmed.
(b) Fix confirmed findings with the fix prompt; for each fix diff, list every caller and feature it can affect.
(c) Turn every repeated bug class into a lint, type or test check.
(d) Write qa/REPORT.md: commit hash, environment, the exact gate and verification commands with exit codes and counts,
    every contract row with VERIFIED / BROKEN / UNPROVEN and its evidence link, what was NOT checked, then
    "assessment complete" and separately "ready for <scope>" only if no P0 row is BROKEN or UNPROVEN.
    Add new bug classes to references/bug-classes.md or to the project's own list.
```

## Fix prompt: one bug, at the end of any step

```text
Fix contract row <ID>. The failing test <name> is the reproducer: show it failing for the reported reason first, make
the smallest fix at the responsible layer, show it passing, then run the gate and report command, commit, exit code
and counts. Do not edit the test or the contract.
If two attempts on the same hypothesis fail, stop and report what you learned.
```
