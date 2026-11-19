"""Count how often an LLM decision system gives the same decision on identical input.

Input: a JSONL file with one line per run, for example
    {"case": "c01", "run": 1, "decision": ["BTC", "ETH"]}
A decision may be a string, a number or a list. The order inside a list is ignored.
Cases with a single run are skipped and counted separately.

Usage: python stability.py runs.jsonl [--stable 0.8] [--unstable 0.5]
       python stability.py --selftest
Exit code: 0 when the verdict is "stable", 1 otherwise.
"""
import argparse
import json
import sys
from collections import defaultdict


def norm(decision):
    return tuple(sorted(map(str, decision))) if isinstance(decision, list) else str(decision)


def score(rows, stable=0.8, unstable=0.5):
    by_case = defaultdict(list)
    for row in rows:
        by_case[row["case"]].append(norm(row["decision"]))
    repeated = [runs for runs in by_case.values() if len(runs) >= 2]
    same = sum(len(set(runs)) == 1 for runs in repeated)
    share = same / len(repeated) if repeated else 0.0
    if not repeated:
        verdict = "no repeated cases"
    elif share >= stable:
        verdict = "stable"
    elif share <= unstable:
        verdict = "unstable"
    else:
        verdict = "inconclusive"
    return {"cases": len(repeated), "same": same, "share": share, "verdict": verdict,
            "skipped": len(by_case) - len(repeated)}


def selftest():
    rows = []
    for i in range(10):
        rows.append({"case": i, "run": 1, "decision": ["A", "B"]})
        rows.append({"case": i, "run": 2, "decision": ["B", "A"] if i < 8 else "C"})
    result = score(rows)
    assert (result["cases"], result["same"], result["verdict"]) == (10, 8, "stable"), result
    assert score(rows[4:])["verdict"] == "inconclusive"   # 6 of 8
    assert score(rows[12:])["verdict"] == "unstable"      # 2 of 4
    assert score(rows[:1]) == {"cases": 0, "same": 0, "share": 0.0, "verdict": "no repeated cases", "skipped": 1}
    print("selftest ok")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("runs", nargs="?", help="JSONL file, one run per line")
    parser.add_argument("--stable", type=float, default=0.8, help="share of cases needed for 'stable' (default 0.8)")
    parser.add_argument("--unstable", type=float, default=0.5, help="share at or below which it is 'unstable' (default 0.5)")
    parser.add_argument("--selftest", action="store_true", help="run the built-in check and exit")
    args = parser.parse_args()
    if args.selftest:
        return selftest()
    if not args.runs:
        parser.error("give a JSONL file or --selftest")
    with open(args.runs, encoding="utf-8") as handle:
        rows = [json.loads(line) for line in handle if line.strip()]
    result = score(rows, args.stable, args.unstable)
    print(f"cases with 2+ runs: {result['cases']} | same decision: {result['same']} ({result['share']:.0%}) | "
          f"single-run cases skipped: {result['skipped']} | verdict: {result['verdict']}")
    sys.exit(0 if result["verdict"] == "stable" else 1)


if __name__ == "__main__":
    main()
