# ICC + OTE TradingView Bot

A **top-down, multi-timeframe** trading bot built around the **ICC** strategy —
*Indication · Correction · Continuation* (Trades by Sci) — blended with **ICT**
concepts (Fair Value Gaps, Order Blocks) and the **OTE** (Optimal Trade Entry)
Fibonacci zone.

Apply it on your **1H chart**: it reads **1D** structure for bias, requires the **4H**
to agree, marks up the **OTE / FVG / order-block** confluence, and enters on the 1H.
Tuned for **MNQ1!, MES1!, XAUUSD, and crypto**.

> ⚠️ Educational template, **not financial advice**. Trading is risky — read
> [`docs/RISK.md`](docs/RISK.md) before using real money.

## What's in the box

| Path | What it is |
|---|---|
| [`pine/ICC_OTE_strategy.pine`](pine/ICC_OTE_strategy.pine) | The main bot: a Pine v5 **strategy** that backtests, plots the OTE zone, and fires JSON alerts. |
| [`pine/ICC_OTE_indicator.pine`](pine/ICC_OTE_indicator.pine) | Alerts-only **indicator** version with the same logic. |
| [`webhook/`](webhook/) | Optional Python **webhook bridge** that receives alerts and can route them to a broker. **Paper-mode by default.** |
| [`docs/ICC_STRATEGY.md`](docs/ICC_STRATEGY.md) | How the strategy thinks + input tuning per market. |
| [`docs/SETUP.md`](docs/SETUP.md) | Step-by-step setup (TradingView first, automation later). |
| [`docs/RISK.md`](docs/RISK.md) | Risk disclaimer. |

## How it trades (top-down)

| Step | Timeframe | What the bot does |
|---|---|---|
| **Bias** | 1D | Reads daily structure (BOS) to set direction |
| **Confirm** | 4H | Requires 4H structure to **match** the 1D bias, else no trade |
| **Markup** | 4H leg | Draws the **entry zone (0.618–0.786)** and the 50% equilibrium |
| **Confluence** | 1H | Requires the entry zone to overlap an **FVG / inverse FVG / rejection block / order block**, in the correct **premium/discount** zone |
| **Entry** | 1H | Limit at the **shallowest of 0.618/0.705/0.786 that still clears 2:1**, in the aligned direction |

Entries fire **only in the London / NY kill zones** (NY emphasised for volume) and only
when a **volume-weighted confluence score** clears a quality bar. They're **limit orders
at the OTE level**, auto-sized to risk **1% of equity**, gated to a **minimum 2:1 R:R**
and a **max of 1–2 trades/day**. Take-profit **scales over up to 3 tranches (1R/2R/4R)**;
the stop moves to **break-even after TP1** and **trails up to TP1 after TP2**, so the
runner rides risk-free. A chart table shows 1D/4H alignment, session, confluence score,
the live setup, and trades-used-today. Full detail in
[`docs/ICC_STRATEGY.md`](docs/ICC_STRATEGY.md).

## Quick start

1. **Load it:** open your **1H chart**, paste `pine/ICC_OTE_strategy.pine` into the
   TradingView Pine Editor → *Add to chart* → check the **Strategy Tester**.
2. **Alert it:** create an alert on *"Any alert() function call"* — get notified (or
   trade manually) whenever 1D+4H align and price taps the OTE zone.
3. **Automate it (optional):** run the webhook bridge in `webhook/` (starts in paper
   mode) and, when ready, wire crypto execution or a futures bridge.

See [`docs/SETUP.md`](docs/SETUP.md) for the walkthrough.

## Why "alerts first"?

TradingView itself **cannot place live orders** — it only fires alerts. Your main
markets (index futures + gold) have **no first-party auto-execution** and often
prop-firm restrictions, so the bot delivers precise signals everywhere and gives you
a safe, gated path to automation (crypto today; futures via a bridge you add). The
webhook never trades until you explicitly set `LIVE_TRADING=true`.
