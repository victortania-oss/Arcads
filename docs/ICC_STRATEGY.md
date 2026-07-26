# The ICC + OTE strategy (how the bot thinks)

This bot codifies the **ICC** framework (*Indication · Correction · Continuation*,
as taught by Trades by Sci) as a **top-down, multi-timeframe** model, fused with
**ICT** confluence tools (Fair Value Gaps, Order Blocks) and the **OTE** (Optimal
Trade Entry) Fibonacci zone.

## Top-down, the way you trade it

Apply the script on your **1H entry chart**. It reads the higher timeframes for you
via `request.security` and only arms a setup when everything lines up:

| Step | Timeframe | What the bot does |
|---|---|---|
| **Bias** | **1D** | Reads daily market structure (break of structure on daily swings) to set the directional bias — bull, bear, or none. |
| **Confirm** | **4H** | Reads 4H structure and requires it to **match** the 1D bias. If they disagree, **no trade is armed**. |
| **Markup** | **4H leg** | Draws the **Fib / OTE zone (0.62–0.79)** and the leg high/low on the aligned 4H impulse. |
| **Confluence** | **1H** | Detects a **Fair Value Gap** and an **order block** on the entry timeframe. |
| **Entry** | **1H** | Fires only when price taps the OTE zone with confluence, in the aligned HTF direction. |

The bias table (top-right of the chart) shows all of this at a glance: 1D bias, 4H
bias, whether they're **Aligned**, and the current **Setup** (LONG / SHORT / wait).

## The three phases

### 1. Indication (1D → 4H)
A **break of structure (BOS)** on the daily signals institutional intent, and the 4H
must confirm the same direction. This is your "structure on 1D, matches on 4H" step.
- **Bullish:** a new swing high takes out the previous swing high (higher-high).
- **Bearish:** a new swing low takes out the previous swing low (lower-low).
- Only when **1D and 4H agree** is a setup armed. This is the single biggest filter —
  it keeps you trading *with* the higher-timeframe order flow.

### 2. Correction (markup + OTE)
The bot draws the **OTE zone** on the aligned 4H leg using Fibonacci:
- **Shallow edge = 0.62**, **deep edge = 0.79**, with the **0.705 sweet spot** plotted
  in orange. The zone shades teal (longs) / red (shorts).
- Highs/lows of the leg are marked. On the 1H it boxes the most recent **FVG** (teal/red)
  and the **order block** (green/maroon) so your confluence is drawn for you.
- **Entry** is the first 1H tap into the OTE zone. If price breaks the leg origin before
  tagging the zone, the setup is **invalidated** and the bot stands down.

### 3. Continuation
- **Stop** sits just beyond the leg origin (the 1.0 Fib), plus a small tick buffer.
- **Target** is a configurable **R multiple** (default 2.5R) as price continues toward
  liquidity beyond the indication swing.

## Inputs cheat-sheet

| Input | What it does | Typical |
|---|---|---|
| Bias timeframe | HTF that sets direction | `1D` |
| Confirmation timeframe | Must agree with bias | `240` (4H) |
| Draw OTE / Fib on | Which HTF leg carries the zone | `Confirmation` (4H) |
| Swing lookback | Strictness of HTF swing detection | 5 |
| OTE shallow / deep | Fib edges of the entry zone | 0.62 / 0.79 |
| Require 1H FVG confluence | Only enter with displacement | On |
| Stop buffer (ticks) | Padding beyond the swing | 4 |
| Target (R multiple) | Reward vs. risk | 2.0–3.0 |

## Tuning per market

- **MNQ1! / MES1!** (index futures): keep 1D/4H bias, enter 1H. Mind tick value when
  reading R. Consider raising swing lookback if the daily is choppy.
- **XAUUSD** (gold): gold wicks hard — a slightly larger stop buffer and swing lookback
  reduce false stops. 1D/4H/1H maps cleanly.
- **Crypto** (BTC/ETH): trades 24/7, so the daily/4H structure is continuous; the same
  1D/4H/1H stack works well.

## A note on higher-timeframe repainting

HTF structure is pulled with `lookahead_off`, and the strategy confirms entries on 1H
**bar close** (`process_orders_on_close=true`). A forming 1D/4H bar can still update
until it closes — so a live bias can shift intra-bar before the HTF candle finishes.
That's normal for MTF tools: treat a signal as final on the close of the 1H entry bar.

> Starting points only. **Backtest each symbol/timeframe** in the Strategy Tester and
> forward-test on demo before trusting a signal. See `docs/RISK.md`.
