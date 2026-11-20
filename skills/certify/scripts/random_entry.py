"""Do a system's picks beat random entries? Replay its closed trades against random ones.

Inputs are CSV files with a header row. Times are ISO 8601 ("2026-10-01T12:00:00Z"; no offset means UTC) or epoch
milliseconds.
    trades.csv   market,entry,exit[,size][,side]   one row per closed trade; size defaults to 1, side to long
    prices.csv   market,time,close                 the candles of every market that was traded
    slots.csv    time                              optional: the moments the system could have decided.
                                                   Default: every candle time between the first entry and last exit.

Three comparisons, each over --runs random replays: same markets at random entry times, same entry times in random
markets, and both at random. A random trade keeps the real trade's size, side and holding time, so both sides pay
the same fees and results are compared before fees. A price is the close of the last candle at or before a moment.

Rule, to be fixed before the first run: the picks add something only if the real result beats at least 95% of the
random runs in one comparison. At 5% or less in all three they are worse than random. Otherwise: no evidence.

Usage: python random_entry.py trades.csv prices.csv [--slots slots.csv] [--runs 10000] [--seed 7] [--out result.md]
       python random_entry.py --selftest
Exit code: 0 when the picks add something, 1 otherwise, 2 when the input cannot be used.
"""
import argparse
import bisect
import csv
import random
import statistics
import sys
from datetime import datetime, timezone
from itertools import pairwise

KINDS = (("time", "Same markets, random entry times"), ("market", "Same entry times, random markets"),
         ("both", "Random times and markets"))
VERDICTS = {"adds": "the picks add something", "worse": "the picks are worse than random",
            "none": "no evidence that the picks add anything"}


def stop(message):
    print(message, file=sys.stderr)
    sys.exit(2)


def ms(text):
    text = str(text).strip()
    if text.lstrip("-").isdigit():
        return int(text)
    stamp = datetime.fromisoformat(text.replace("Z", "+00:00"))
    return round((stamp if stamp.tzinfo else stamp.replace(tzinfo=timezone.utc)).timestamp() * 1000)


class Prices:
    def __init__(self, rows):
        """rows: (market, time in ms, close)."""
        self.d = {}
        for market, moment, close in sorted(rows):
            times, closes = self.d.setdefault(market, ([], []))
            times.append(moment)
            closes.append(close)
        self.reach = {m: 4 * statistics.median(b - a for a, b in pairwise(ts))
                      for m, (ts, _) in self.d.items() if len(ts) > 1}

    def at(self, market, moment):
        """Close of the last candle at or before the moment; None outside the data or over 4 candles after it."""
        times, closes = self.d.get(market, ([], []))
        i = bisect.bisect_right(times, moment) - 1
        if i < 0 or moment - times[i] > self.reach.get(market, 0):
            return None
        return closes[i]

    def ret(self, market, start, end):
        a, b = self.at(market, start), self.at(market, end)
        return None if a is None or b is None or a == 0 else b / a - 1


def pct(sorted_xs, q):
    return sorted_xs[min(len(sorted_xs) - 1, int(q * len(sorted_xs)))]


def compare(trades, prices, slots=None, runs=10_000, seed=7):
    """trades: dicts with market, t0, t1, size, sign (+1 long, -1 short). Returns the figures of the report."""
    usable = []
    for t in trades:
        r = prices.ret(t["market"], t["t0"], t["t1"])
        if r is not None:
            usable.append({**t, "ret": r})
    if not usable:
        stop("no trade has prices at both its entry and its exit: check the markets and times")
    real = sum(t["size"] * t["sign"] * t["ret"] for t in usable)
    universe = sorted({t["market"] for t in trades})
    if slots is None:
        first, last = min(t["t0"] for t in usable), max(t["t1"] for t in usable)
        slots = sorted({m for market in universe for m in prices.d.get(market, ([], []))[0] if first <= m <= last})
    rng = random.Random(seed)

    def draw(kind):
        total = 0.0
        for t in usable:
            for _ in range(50):  # retry until the random pick has prices
                start = rng.choice(slots) if kind != "market" else t["t0"]
                market = rng.choice(universe) if kind != "time" else t["market"]
                r = prices.ret(market, start, start + t["t1"] - t["t0"])
                if r is not None:
                    total += t["size"] * t["sign"] * r
                    break
        return total

    rows = []
    for kind, label in KINDS:
        xs = sorted(draw(kind) for _ in range(runs))
        rows.append({"label": label, "median": statistics.median(xs), "low": pct(xs, 0.05), "high": pct(xs, 0.95),
                     "beats": sum(x < real for x in xs) / runs})
    best = max(row["beats"] for row in rows)
    return {"trades": len(trades), "usable": len(usable), "real": real, "slots": len(slots), "markets": len(universe),
            "runs": runs, "rows": rows, "verdict": "adds" if best >= 0.95 else "worse" if best <= 0.05 else "none"}


def report(result):
    lines = [f"# Do the picks beat random entries? ({result['usable']} of {result['trades']} trades with prices)", "",
             f"- Real trades, replayed on the given prices: {result['real']:+.2f} before fees",
             f"- Decision slots: {result['slots']}; markets: {result['markets']}", ""]
    for row in result["rows"]:
        lines.append(f"- {row['label']}: median {row['median']:+.2f}, middle 90% from {row['low']:+.2f} to "
                     f"{row['high']:+.2f}. The real trades beat {row['beats']:.1%} of {result['runs']:,} random runs.")
    lines += ["", ("Verdict by the rule fixed beforehand (beat at least 95% of random runs): "
                   f"{VERDICTS[result['verdict']]}.")]
    if result["usable"] < 30:
        lines.append("Fewer than 30 trades: only a very large difference can show at this size.")
    return "\n".join(lines) + "\n"


def read(path, *columns):
    with open(path, encoding="utf-8-sig", newline="") as handle:
        rows = [{(k or "").strip().lower(): (v or "").strip() for k, v in row.items()} for row in csv.DictReader(handle)]
    missing = [c for c in columns if not rows or c not in rows[0]]
    if missing:
        stop(f"{path}: needs a header row with the columns {', '.join(columns)}; missing: {', '.join(missing)}")
    return rows


def load(trades_path, prices_path, slots_path=None):
    trades = [{"market": r["market"], "t0": ms(r["entry"]), "t1": ms(r["exit"]), "size": float(r.get("size") or 1),
               "sign": -1 if r.get("side", "").lower() in ("short", "sell") else 1}
              for r in read(trades_path, "market", "entry", "exit")]
    prices = Prices((r["market"], ms(r["time"]), float(r["close"])) for r in read(prices_path, "market", "time", "close"))
    slots = [ms(r["time"]) for r in read(slots_path, "time")] if slots_path else None
    return trades, prices, slots


def selftest():
    hour = 3_600_000
    assert ms("2026-01-01T00:00:00Z") == ms("2026-01-01T01:00:00+01:00") == ms("1767225600000") == 1_767_225_600_000
    # Market A rises 1% in every hour that starts at a multiple of 10 and falls 1% in the hour that starts 5 later.
    # Market B never moves.
    price, rows = 100.0, []
    for h in range(401):
        rows += [("A", h * hour, price), ("B", h * hour, 50.0)]
        price *= 1.01 if h % 10 == 0 else 0.99 if h % 10 == 5 else 1.0
    prices = Prices(rows)
    assert prices.at("A", 400 * hour + 4 * hour) is not None and prices.at("A", 400 * hour + 5 * hour) is None
    assert prices.at("A", -1) is None and prices.ret("C", 0, hour) is None
    slots = [h * hour for h in range(400)]
    trade = lambda h, sign=1: {"market": "A", "t0": h * hour, "t1": (h + 1) * hour, "size": 100.0, "sign": sign}
    winners = compare([trade(h) for h in range(0, 400, 10)], prices, slots, runs=300)
    assert winners["verdict"] == "adds" and abs(winners["real"] - 40.0) < 1e-6, winners
    assert all(row["beats"] >= 0.95 for row in winners["rows"]), winners["rows"]
    losers = compare([trade(h) for h in range(5, 400, 10)], prices, slots, runs=300)
    assert losers["verdict"] == "worse" and abs(losers["real"] + 40.0) < 1e-6, losers
    shorts = compare([trade(h, -1) for h in range(5, 400, 10)], prices, slots, runs=300)
    assert shorts["verdict"] == "adds" and abs(shorts["real"] - 40.0) < 1e-6, shorts  # a short gains when the price falls
    # A market that only falls: shorts spread evenly earn what random shorts earn, so no evidence either way.
    fall, rows = 100.0, []
    for h in range(401):
        rows.append(("D", h * hour, fall))
        fall *= 0.999 if h % 2 else 0.997
    drift = compare([{**trade(h, -1), "market": "D"} for h in range(40)], Prices(rows), slots, runs=300)
    assert drift["real"] > 0 and drift["verdict"] == "none", drift
    rng = random.Random(1)
    blind = compare([trade(rng.randrange(400)) for _ in range(40)], prices, slots, runs=300)
    assert blind["verdict"] == "none", blind
    default_slots = compare([trade(h) for h in range(0, 400, 10)], prices, runs=50)
    assert default_slots["slots"] == 392 and default_slots["verdict"] == "adds", default_slots
    out_of_data = compare([trade(0), trade(900)], prices, slots, runs=10)
    assert (out_of_data["trades"], out_of_data["usable"]) == (2, 1)
    assert "1 of 2 trades" in report(out_of_data) and "Fewer than 30 trades" in report(out_of_data)
    print("selftest ok")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("trades", nargs="?", help="CSV: market,entry,exit[,size][,side]")
    parser.add_argument("prices", nargs="?", help="CSV: market,time,close")
    parser.add_argument("--slots", help="CSV with a column time: the moments the system could have decided")
    parser.add_argument("--runs", type=int, default=10_000, help="random replays per comparison (default 10000)")
    parser.add_argument("--seed", type=int, default=7, help="seed of the random draws (default 7)")
    parser.add_argument("--out", help="also write the report to this file")
    parser.add_argument("--selftest", action="store_true", help="run the built-in check and exit")
    args = parser.parse_args()
    if args.selftest:
        return selftest()
    if not args.trades or not args.prices:
        parser.error("give trades.csv and prices.csv, or --selftest")
    try:
        result = compare(*load(args.trades, args.prices, args.slots), runs=args.runs, seed=args.seed)
    except (OSError, ValueError, KeyError) as problem:
        stop(f"cannot use the input: {problem}")
    text = report(result)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as handle:
            handle.write(text)
    print(text, end="")
    sys.exit(0 if result["verdict"] == "adds" else 1)


if __name__ == "__main__":
    main()
