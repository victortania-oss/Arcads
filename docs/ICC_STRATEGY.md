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

### 2b. Golden pocket, Premium/Discount & confluence AT the pocket

This is the heart of the entry model, and the bot now enforces it precisely — it will
**not** enter just because confluences exist *nearby*; they must sit *in the pocket*, in
the right half of the range:

- **Golden pocket (0.618–0.65).** The default entry is the golden pocket, not the broad
  OTE. It's drawn as a **yellow band**, with the resting limit order inside it.
- **Premium / Discount (50% equilibrium).** The bot marks the **equilibrium** (50% of the
  dealing range = the HTF leg, per your notes: swing-high→swing-low). **Longs only fire in
  discount** (below equilibrium); **shorts only in premium** (above). Turn off with
  *Require correct Premium/Discount*.
- **Confluence AT the pocket (spatial, not just present).** With *Require a confluence at
  the golden pocket* on, an entry needs the pocket to **overlap a confluence zone**:
  - **Fair Value Gap** (the 3-candle imbalance band)
  - **Inverse FVG** — an opposite-side FVG that got closed through and flipped to support/
    resistance
  - **Rejection block** — the *wick* left when price traded into a level and was rejected,
    then displaced away (wick area, not the body — per your notes)
  - **Order block** — the last opposite candle before displacement (strongest when paired
    with a liquidity sweep)

  The overlap is a true band-intersection test with a freshness window, so "the pocket
  sits in an FVG / IFVG / OB / rejection block" is checked literally.
- The chart table shows **P / D zone** (discount ✓ / premium ✓) and **Pocket conf**
  (AT pocket ✓ / none) live, so you can see the setup qualify in real time.

### 2. Correction (markup + OTE)
The bot draws the **OTE zone** on the aligned 4H leg using Fibonacci:
- **Shallow edge = 0.62**, **deep edge = 0.79**, with the **0.705 sweet spot** plotted
  in orange. The zone shades teal (longs) / red (shorts).
- Highs/lows of the leg are marked. On the 1H it boxes the most recent **FVG** (teal/red)
  and the **order block** (green/maroon) so your confluence is drawn for you.
- **Entry is a resting limit order** placed at your chosen Fib level (the magenta line —
  default the **0.705 sweet spot**). You are filled *only if price trades into the zone*;
  if it doesn't, the order is cancelled and nothing happens. This is the authentic OTE
  entry and makes the backtest honest (no filling at a worse "market" price). If price
  breaks the leg origin before reaching the level, the setup is **invalidated**.

### 3. Continuation (scaled exits + break-even)
- **Stop** sits just beyond the leg origin (the 1.0 Fib), plus a small tick buffer.
- **Take-profit is scaled over up to 3 tranches** (R-multiples of the stop distance,
  defaults **1R / 2R / 3R**). You choose what % closes at TP1 and TP2 (default 50% /
  30%); TP3 — the **runner** — closes the remainder.
- **Break-even after TP1:** the moment price prints TP1, the stop jumps to your entry
  (plus an optional tick offset to cover fees). From there the runner is a **risk-free
  trade** — exactly the "third level is basically risk-free" management. Turn it off with
  *Move stop to break-even after TP1*.
- On the chart while in a trade: **green lines** mark TP1/TP2/TP3 and the **stop line**
  turns from red to **yellow** once it's at break-even.

**Reading the tranches:** set *Take-profit tranches* to 1 for a single target, 2 for
two, or 3 for the full risk-free-runner model. The webhook alert JSON carries `sl`,
`tp1`, `tp2`, `tp3` so an execution bridge can replicate the same scaling live.

## Risk model (position sizing + limits)

The strategy sizes and gates every trade to a fixed risk profile:

- **1% risk per trade (auto-sizing).** Position size is *calculated*, not fixed: the bot
  works out how many contracts make a full stop-out cost exactly **1% of account equity**
  (`Risk per trade (%)`). Wider stop → fewer contracts; tighter stop → more. Turn on
  *Round size to whole contracts* for futures (MNQ/MES); off for crypto/forex where
  fractional size is fine. If 1% risk can't fund even one contract, the trade is skipped
  rather than over-risked.
- **Minimum R:R gate (2:1).** A setup is only taken if the **runner target ≥ Minimum R:R**
  (default 2.0). Since the runner defaults to 4R, this passes normally — but if you tighten
  the targets below 2R, the bot stands down instead of taking a sub-2:1 trade.
- **Max trades per day (1–2).** Once `Max trades per day` entries have filled, no new
  entries fire until the next day. The chart table shows **Trades today: n / max**.
- **Staged stop protection.**
  - After **TP1** → stop to **break-even** (risk-free runner).
  - After **TP2** → stop trails up to the **TP1 price**, locking in profit on the runner
    (toggle: *Trail stop up to TP1 after TP2*).
  - With a **higher TP3** (default 4R) the runner has room to reach for the big move while
    your downside is already removed.

> **Futures sizing note:** tranche percentages split the position by contract count. For
> MNQ/MES, size so the splits land on **whole contracts** (e.g. 4 contracts → 50/25/25),
> otherwise the backtester rounds fractional lots. Also sanity-check `syminfo.pointvalue`
> for your symbol — the 1% sizing depends on it, and CFD/forex feeds vary.

## Liquidity sweep filter (optional ICT refinement)

Turn on **Require liquidity sweep before entry** to demand a **stop raid** before you
commit — a hallmark of the ICT entry model:

- **Longs:** the correction must first dip **below a prior minor 1H swing low** and
  **close back above it** (sweeping resting sell-side liquidity) before the OTE tap.
- **Shorts:** mirror — sweep a prior minor 1H swing high and close back below it.
- A small **⨯** marks each qualifying sweep on the chart. The sweep stays valid for
  *N* bars (default 10) so the entry can follow shortly after the raid.

Inputs: *Minor swing lookback (1H)* controls how significant the swept level must be
(default 3); *Sweep valid for N bars* is the window. This filter cuts trades but tends
to improve entry quality — backtest it on/off per symbol.

## Sessions + confluence priority

The bot trades **only the London and New York kill zones**, and prioritises the
highest-quality setups — which matters because you're capped at 1–2 trades a day.

- **Kill-zone gating.** With *Trade only London / NY* on, no entry fires outside the
  **London (02:00–05:00)** or **New York (07:00–10:00)** windows. Times are read in the
  *Session timezone* (default `America/New_York`) so they're the same regardless of the
  symbol's exchange. Adjust the windows to your exact kill zones.
- **NY emphasis.** With *Emphasize NY* on, London-only hours require **one extra
  confluence** to trade, so the higher-volume NY session gets the lighter filter and the
  priority.
- **Confluence score (volume-weighted).** Every setup is scored:

  | Confluence | Points |
  |---|---|
  | Fair Value Gap on the leg | 1 |
  | Order-block retest (price in the OB) | 1 |
  | Liquidity sweep before entry | 1 |
  | **Above-average volume** | **2** (double-weighted) |

  Only setups scoring **≥ Minimum confluences** (default 2) are taken. Volume counts
  double, so a volume-backed setup clears the bar on its own — directly encoding
  "prioritise trades where the confluences match, especially with volume." Set
  *Require above-average volume* on to make volume mandatory rather than just weighted.
- The chart table shows the live **Session**, the **Confluence** score vs. what's
  required (with a ⚡ when volume is elevated), and trades used today.

> Kill-zone defaults are the classic ICT windows. If you trade the NY afternoon or the
> London open differently, widen/split the sessions to match your plan.

## Inputs cheat-sheet

| Input | What it does | Typical |
|---|---|---|
| Bias timeframe | HTF that sets direction | `1D` |
| Confirmation timeframe | Must agree with bias | `240` (4H) |
| Draw OTE / Fib on | Which HTF leg carries the zone | `Confirmation` (4H) |
| Swing lookback | Strictness of HTF swing detection | 5 |
| OTE shallow / deep | Fib edges of the entry zone | 0.62 / 0.79 |
| Limit entry level | Fib level the resting order sits at | 0.618 (golden pocket) |
| Golden pocket shallow / deep | Pocket band edges | 0.618 / 0.65 |
| Require correct Premium/Discount | Long in discount, short in premium | On |
| Require a confluence at the golden pocket | Pocket must overlap FVG/IFVG/OB/rejection | On |
| Confluence zone valid for N bars | Freshness of a confluence zone | 40 |
| Require 1H FVG confluence | Only enter with displacement | On |
| Require liquidity sweep | Demand a stop raid first | Off (test per symbol) |
| Minor swing lookback (1H) | Significance of swept level | 3 |
| Trade only London / NY | Kill-zone gating | On |
| London / NY kill zone | Session windows (session TZ) | 0200–0500 / 0700–1000 |
| Emphasize NY | Stricter confluence in London | On |
| Volume threshold (× avg) | Bar volume to count as elevated | 1.0 |
| Minimum confluences to trade | Quality gate (volume ×2) | 2 |
| Require above-average volume | Make volume mandatory | Off |
| Risk per trade (%) | Equity risked on a full stop-out | 1.0 |
| Round size to whole contracts | Futures on, crypto/forex off | On |
| Minimum R:R | Skip if runner target below this | 2.0 |
| Max trades per day | Daily entry cap | 2 |
| Stop buffer (ticks) | Padding beyond the swing | see presets |
| Take-profit tranches | How many scale-out targets | 3 |
| TP1 / TP2 / TP3 (R) | Target distances in R | 1 / 2 / 4 |
| Close at TP1 / TP2 (%) | Portion exited at each | 50 / 30 (rest at TP3) |
| Move stop to break-even after TP1 | Risk-free runner | On |
| Trail stop up to TP1 after TP2 | Lock profit on runner | On |
| Break-even offset (ticks) | Cover fees past entry | 0 |

## Per-market presets (starting points)

Copy these into the inputs, then backtest and adjust. "Stop buffer" is in **ticks**
(the instrument's `mintick`), so it scales to each symbol automatically.

| Setting | **MNQ1!** (Micro Nasdaq) | **MES1!** (Micro S&P) | **XAUUSD** (Gold) | **Crypto** (BTC/ETH) |
|---|---|---|---|---|
| Bias / Confirm / Entry | 1D / 4H / 1H | 1D / 4H / 1H | 1D / 4H / 1H | 1D / 4H / 1H |
| Swing lookback | 5 | 5 | 6–7 | 5 |
| OTE shallow / deep | 0.62 / 0.79 | 0.62 / 0.79 | 0.62 / 0.79 | 0.62 / 0.79 |
| Require 1H FVG | On | On | On | On |
| Require liquidity sweep | Optional | Optional | **On** (gold loves stop raids) | Optional |
| Minor swing lookback | 3 | 3 | 3–4 | 3 |
| Stop buffer (ticks) | 8 (≈2.0 pts) | 8 (≈2.0 pts) | 20 (≈$2.00) | 10 |
| Risk per trade | 1% | 1% | 1% | 1% |
| TP tranches (R) | 1 / 2 / 4 | 1 / 2 / 4 | 1 / 2 / 4 | 1 / 2.5 / 5 |
| Close % at TP1 / TP2 | 50 / 30 | 50 / 30 | 50 / 25 | 40 / 30 |
| Break-even after TP1 | On | On | On | On |
| Max trades/day | 2 | 2 | 2 | 2 |

Rationale:
- **XAUUSD** wicks aggressively and raids liquidity often → wider stop buffer, a higher
  swing lookback to ignore noise, and the sweep filter on.
- **MNQ vs MES**: same structure, but MNQ moves ~4× the points of MES per unit — the
  tick-based buffer keeps risk comparable. Watch tick value when sizing.
- **Crypto** trends hard and runs 24/7 → a higher target (3R) captures the continuation.

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
