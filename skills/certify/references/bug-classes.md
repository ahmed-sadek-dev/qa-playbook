# Bug classes

26 bug types found while certifying two AI-built trading apps: a charting and paper-trading desktop app (B1 to B16) and a broker bot with its scanner and monitor (B17 to B26). The same AI tends to repeat the same mistake across projects, so step 4 checks every later project for each class. Each entry gives the pattern and the check that catches it. The sections below group the classes by topic, so the numbers are not in order.

## Data and bars

- **B1 Old data used as live.** A feed re-sends older bars and the consumer treats any bar as the current price. Check: feed [older bar, newer bar, older bar again]; the price or fill must follow the newest bar time only.
- **B7 Gap never backfilled.** A stream reconnects after an outage and the missing bars are never fetched, so indicators run on a series with holes. Check: push bar t, then t+2; the missing bar must be fetched and evaluated in order.
- **B8 Edge case differs from the reference.** An indicator matches the reference on normal data but not on degenerate input. Check: run each indicator on flat, constant-zero and too-short series and compare with the reference.
- **B10 Bar close detected late.** "On bar close" fires only when the next bar's first tick arrives, so a Friday close fires on Monday. Check: what fires at a session close with no further ticks.
- **B14 Feed points that are not bars.** A source appends non-bar points (a session-end marker, an off-grid latest quote) and the app shows them as bars. Check on live data: no bar outside the selected session, every bar time on the interval grid, and the last price unchanged.
- **B19 Forming bar treated as finished.** Logic that needs completed bars includes the still-forming bar, so it acts one bar early. Check: feed a last bar that is still forming and changes afterwards; the decision must not change until it completes.

## Orders and money

- **B2 Already-triggered order accepted.** A stop that the current price has already passed fills instantly at the trigger price, often at a fake profit, instead of being rejected. Check: place and modify stops on both sides of the market, buy and sell, live and replay.
- **B4 Child orders not following the parent.** Take-profit or stop orders keep the original size when the position grows, flips or is replaced. Check: add to a position, then trigger the protection; the position must be flat.
- **B5 Simulated fill outside the bar.** A replay or backtest fills at a price the bar never traded. Check: assert every simulated fill lies within the low and high of its bar.
- **B6 Risk check blocks reducing risk.** A buying-power or size check rejects closing a losing position, so the loss can never be closed. Check: close a deep losing position, long and short; the close must be accepted.
- **B18 Hidden default or crash for a missing money setting.** A missing size or risk setting silently falls back to a hard-coded number, or an empty value crashes the whole cycle, protection included. Check: remove, empty and corrupt each money setting; no new risk is taken, one alert is sent, and protection of open positions keeps running.
- **B25 One position counted as several trades.** A late fill of the same entry is paired as a separate trade, which changes win rate and profit factor. Check: split one entry into two fills; the summary must show one trade at the average price.

## Restarts, schedules and side effects

- **B3 Catch-up burst.** After a restart or pause, replaying missed history drives real side effects once per historical event. Check: restart with a long gap; count deliveries, not just log rows.
- **B22 Missed scheduled run without an alert.** A slot skipped because a lock was busy or a run was killed simply disappears, and a monitor may even show it as running. Check: block each scheduled slot until its window ends; exactly one "missed" alert, and no "running now" for an ended window.
- **B23 Crash between side effect and saved state repeats the side effect.** A message or order is sent, the process dies before the state records it, and the next run sends it again. Check: kill the process at each point between "send" and "save", restart, and count messages and orders; exactly one.
- **B24 Market calendar ignored.** Schedules assume Monday to Friday trading: they run, alert or show red on holidays and keep slots after an early close. Check: run a fixed-clock day on a holiday and on an early-close day; no runs, no red, no slots after the close.

## Safety guards

- **B17 Safety guard trusts a setting instead of the fact.** An account guard checks a config flag rather than the thing it protects, so a changed flag disables it. Check: flip every safety flag to its unsafe value with the real fact unchanged; the guard must still refuse on the fact.
- **B21 Safety state cleared by a reconnect or restart.** A latched red state is reset by a disconnect, so the card turns green without the cause being fixed. Check: after a red safety verdict, drop and restore the connection and restart the process; the verdict stays red until fresh evidence clears it.

## Screens and reports

- **B9 Search limited to the visible window.** "Next event" or "latest value" looks only inside the displayed page or week, so it shows nothing near the edge. Check: run the UI test on a weekend or at the window edge, or with a fixed clock there.
- **B11 Stale queued work not cancelled.** A view change leaves the old view's requests in a rate-limited queue, so the new view waits behind work nobody needs. Check: change the view while history is still loading; count old-view requests sent after the change and time the new view's first paint.
- **B12 Own cancel reported as a failure.** Closing your own socket or request while it connects fires an error event, and the consumer marks the source down or reconnects. Check: unsubscribe while connecting; no error and no reconnect, while a real failure still reports and retries.
- **B13 First visible item off by one.** "First visible" taken from the floor of a fractional index picks the item just outside the window. Check: pan so an item sits just inside the edge; the reference must be that item, also when the index is an exact integer.
- **B20 Narrow or failed input reported as a quiet result.** A scan that read only the first rows, or could not parse any row, reports "nothing found", which reads as a quiet market. Check: make the source return few rows, unparseable rows and all errors; the result must be an error or state its coverage.
- **B26 Unreadable or stale source shown as a healthy value.** A dashboard shows "no open positions" when the book cannot be read, or "active" when the last cycle is old. Check: corrupt the source file and stop the producer; the screen must say "unknown" or "stale", never a normal value.

## Tests

- **B15 Test depends on the market or the clock.** A test passes only if price moves one way, on a trading day, or at certain hours. Check: run every live test on a weekend and in a falling market; run date-based tests just after 00:00 UTC or with a fixed clock.
- **B16 Suite breaks under machine load.** End-to-end tests pass alone on a quiet machine but fail when the CPU is busy. Check: run 5 full runs on a quiet machine and one full run under load; never read a loaded run as a regression without a same-load baseline.
