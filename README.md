# ICC + OTE TradingView Bot

A trading bot built around the **ICC** strategy — *Indication · Correction ·
Continuation* (Trades by Sci) — blended with **ICT** concepts (Fair Value Gaps,
Order Blocks) and the **OTE** (Optimal Trade Entry) Fibonacci zone.

It works on any TradingView symbol and is tuned for **MNQ1!, MES1!, XAUUSD, and
crypto**.

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

## How it trades

1. **Indication** — a break of structure (higher-high / lower-low swing) signals
   institutional intent, optionally confirmed by a Fair Value Gap.
2. **Correction** — price retraces into the **0.62–0.79 OTE zone** of the indication
   leg. That touch is the entry.
3. **Continuation** — stop sits beyond the leg origin; target is a configurable
   R-multiple (default 2.5R) as price continues toward liquidity.

Full detail in [`docs/ICC_STRATEGY.md`](docs/ICC_STRATEGY.md).

## Quick start

1. **Load it:** paste `pine/ICC_OTE_strategy.pine` into the TradingView Pine Editor
   → *Add to chart* → check the **Strategy Tester**.
2. **Alert it:** create an alert on *"Any alert() function call"* — get notified (or
   trade manually) on every ICC signal.
3. **Automate it (optional):** run the webhook bridge in `webhook/` (starts in paper
   mode) and, when ready, wire crypto execution or a futures bridge.

See [`docs/SETUP.md`](docs/SETUP.md) for the walkthrough.

## Why "alerts first"?

TradingView itself **cannot place live orders** — it only fires alerts. Your main
markets (index futures + gold) have **no first-party auto-execution** and often
prop-firm restrictions, so the bot delivers precise signals everywhere and gives you
a safe, gated path to automation (crypto today; futures via a bridge you add). The
webhook never trades until you explicitly set `LIVE_TRADING=true`.
