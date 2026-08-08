# Risk disclaimer — read before using real money

This project is an **educational trading tool / template**. It is **not financial
advice**, and nothing here is a recommendation to buy or sell any instrument.

- **Trading is risky.** Futures (MNQ, MES), gold (XAUUSD), and crypto are leveraged
  and volatile. You can lose more than you deposit. Only risk money you can afford
  to lose entirely.
- **No guarantees.** Backtest and past performance do **not** predict future results.
  A strategy that backtests well can lose in live markets.
- **Automation multiplies mistakes.** A bug, a bad input, a connectivity drop, or an
  unexpected market condition can cause rapid, real losses. The live path is
  intentionally gated behind `LIVE_TRADING=true` and starts in paper mode.
- **You are responsible.** Test on demo/sandbox accounts first, start with the
  smallest size, use stops, and monitor the system. Verify every fill.
- **Know the rules.** Prop firms and brokers have specific rules about automated
  trading, EAs/bots, and copy execution. Automating against those rules can void
  your account. Check before you connect anything.
- **Software is provided "as is",** without warranty of any kind. The authors are
  not liable for any losses arising from its use.

By using this code you accept full responsibility for your own trading decisions.
