# The ICC + OTE strategy (how the bot thinks)

This bot codifies the **ICC** framework (*Indication · Correction · Continuation*,
as taught by Trades by Sci) and fuses it with **ICT** confluence tools (Fair Value
Gaps, Order Blocks) and the **OTE** (Optimal Trade Entry) Fibonacci zone.

## The three phases

### 1. Indication
A **break of structure (BOS)** signals that institutions have stepped in and a new
direction is likely.

- **Bullish indication:** a new swing high prints *above* the previous swing high
  (higher-high). The bot detects swings with `ta.pivothigh/pivotlow` (the *Swing
  lookback* input controls how strict a swing must be).
- **Bearish indication:** a new swing low prints *below* the previous swing low.
- **FVG confluence (optional):** if *Require Fair Value Gap* is on, the bot only
  arms a setup when a 3-candle imbalance formed on the indication leg — evidence of
  the displacement ICT looks for.

### 2. Correction
After the indication, price pulls back. The bot draws the **OTE zone** on the
indication leg using Fibonacci:

- **Shallow edge = 0.62 retracement**, **Deep edge = 0.79 retracement** (both
  adjustable). The 0.705 "sweet spot" sits in the middle.
- The zone is shaded teal (longs) or red (shorts) on the chart.
- **Entry** triggers the first time price trades into the zone (touches the shallow
  edge) — this is your correction-into-discount (longs) or correction-into-premium
  (shorts).
- If price instead breaks the leg origin before tagging the zone, the setup is
  **invalidated** (structure failed) and the bot stands down.

### 3. Continuation
Once filled, the trade rides the continuation:

- **Stop** goes just beyond the leg origin (swing low for longs, swing high for
  shorts), with a small tick buffer so wicks don't clip it.
- **Target** is a multiple of the stop distance — the *Target (R multiple)* input,
  default **2.5R**. Because OTE entries sit deep in the leg, reaching the prior
  liquidity high/low is often already ~2R, and the continuation runs beyond it.

## Inputs cheat-sheet

| Input | What it does | Typical |
|---|---|---|
| Swing lookback | Strictness of swing detection | 5 (raise to 8–10 on 1m noise) |
| OTE shallow / deep | Fib edges of the entry zone | 0.62 / 0.79 |
| Require FVG confluence | Only trade legs with displacement | On |
| Stop buffer (ticks) | Padding beyond the swing | 4 |
| Target (R multiple) | Reward vs. risk | 2.0–3.0 |
| Session filter | Restrict to a kill zone | Off, or NY 0930–1600 |

## Tuning per market

- **MNQ1! / MES1!** (index futures): 1–5 min charts, session filter to the RTH open
  kill zone often helps. Watch the tick value when reading R.
- **XAUUSD** (gold): 1–15 min; gold wicks hard, so a slightly larger stop buffer and
  swing lookback reduce false stops.
- **Crypto** (BTC/ETH): 5–15 min; trades 24/7 so leave the session filter off.

> These are starting points. **Backtest each symbol/timeframe** in the TradingView
> Strategy Tester and adjust before trusting a signal.
