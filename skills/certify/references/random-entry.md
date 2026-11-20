# Do the picks beat random entries?

Read this when the project picks trades, assets or entry times, by fixed rules or by an LLM.

Code can do exactly what was promised while its picks are no better than chance. This check asks one question: do the real picks beat random picks made under the same conditions? It does not show that a strategy makes money after costs.

## Rule first

Write the rule in `qa/` before the first run. A default:

- adds something: the real result beats at least 95% of the random runs in at least one comparison
- worse than random: 5% or less in all three comparisons
- anything else: no evidence either way

Fix at the same time, and change none of it after the first run: which trades count, the price source and candle size, the decision slots, the seed and the number of runs. Use the trades of one rule version only; mixed versions mix two systems.

## Input: three CSV files

- `trades.csv` with `market,entry,exit[,size][,side]`: one row per closed trade. Size defaults to 1, side to long.
- `prices.csv` with `market,time,close`: candles of every traded market. A market counts as tradable only where it has prices, so leave out candles from before the system could trade it.
- `slots.csv` with `time` (optional): the moments the system could have decided, such as the start of each run. The default is every candle time in the period.

Times are ISO 8601 or epoch milliseconds. Only one small exporter is project-specific: it writes these files from the project's own records, read-only. Keep it in `qa/`.

## Run

```
python <skill folder>/scripts/random_entry.py qa/evidence/trades.csv qa/evidence/prices.csv --slots qa/evidence/slots.csv --out qa/evidence/random-entry.md
```

`--help` lists the options. `--selftest` checks the script itself.

Each random trade keeps a real trade's size, side and holding time. The check therefore tests the choice of market and moment, not exits or sizing, and it compares both sides before fees.

## Record

If the project claims that its picks add value, record that contract row as VERIFIED (adds something), BROKEN (worse than random) or UNPROVEN (no evidence). With fewer than 30 trades, write that only a very large difference can show.
