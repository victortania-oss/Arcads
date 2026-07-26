# Setup guide

Two parts: (A) load the bot on TradingView, and (B) — optional, later — run the
webhook bridge for auto-execution.

---

## A. TradingView (start here)

### 1. Add the script
1. Open TradingView → **Pine Editor** (bottom panel).
2. Paste the contents of **`pine/ICC_OTE_strategy.pine`** (backtest + alerts) or
   **`pine/ICC_OTE_indicator.pine`** (alerts only).
3. Click **Add to chart**.

### 2. Backtest it
- Open the **Strategy Tester** tab. Review net profit, win rate, max drawdown, and
  the list of trades. Do this on **each symbol and timeframe** you trade
  (MNQ1!, MES1!, XAUUSD, BTCUSD…).
- Tune the inputs (gear icon) per `docs/ICC_STRATEGY.md`.

> ⚠️ Backtest results are historical and *not* a promise of future results. The
> strategy uses `process_orders_on_close=true` to avoid look-ahead bias, but always
> forward-test on a demo before risking money.

### 3. Create the alert
1. Click the **⏰ Alert** button.
2. **Condition:** your script → for the strategy pick **"Any alert() function
   call"**; for the indicator pick **"ICC-OTE Long"/"ICC-OTE Short"**.
3. **Notifications:** enable **Webhook URL** only when you've done part B. Otherwise
   use app/email/pop-up notifications and trade manually.
4. The alert message is already JSON — leave it as-is.

That's a fully working alert bot. **You can stop here** and place trades manually
from the alerts. Everything below is for automation.

---

## B. Webhook bridge (optional automation)

### 1. Run the server
```bash
cd webhook
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # then edit .env (set a long WEBHOOK_SECRET)
uvicorn server:app --host 0.0.0.0 --port 8000
```
Check it: open `http://localhost:8000/` → should show `"status":"ok"` and
`"live_trading": false` (paper mode).

### 2. Expose it to TradingView
TradingView must reach your server over **HTTPS on a public URL**. Options:
- A small cloud VM / container with a domain + TLS (Caddy/Nginx), or
- A tunnel for testing: `ngrok http 8000` (gives you an https URL).

Put this in the TradingView alert's **Webhook URL**:
```
https://<your-host>/webhook?secret=<WEBHOOK_SECRET>
```

### 3. Verify in paper mode
Fire a test alert (or curl):
```bash
curl -X POST "http://localhost:8000/webhook?secret=<WEBHOOK_SECRET>" \
  -H "Content-Type: application/json" \
  -d '{"strategy":"ICC-OTE","ticker":"BINANCE:BTCUSDT","action":"buy","price":65000,"sl":64000,"tp":68000}'
```
You'll see it logged to `signals.log` with `"live": false`. Nothing is traded.

### 4. Go live — deliberately

**Crypto (supported out of the box via ccxt):**
1. In `.env`: `BROKER=crypto`, fill `CCXT_EXCHANGE/API_KEY/SECRET`, keep
   `CCXT_SANDBOX=true`, set a tiny `ORDER_QUOTE_AMOUNT`.
2. Set `LIVE_TRADING=true` and restart.
3. Test thoroughly on the exchange **testnet** before switching `CCXT_SANDBOX=false`.

**Futures (MNQ1!, MES1!) and XAUUSD:** TradingView has no first-party auto-execution
for these, and prop-firm rules often forbid or restrict automation. You need a
third-party execution bridge, e.g.:
- Tradovate / NinjaTrader / Rithmic-connected bridges,
- A broker with a REST API + a custom adapter.

To add one, drop a new adapter in `webhook/brokers/` implementing
`execute(signal) -> dict` (see `brokers/paper.py`) and register it in
`brokers/__init__.py`. **Check your broker's and prop firm's rules on automated
trading first.**

---

## Security notes
- Keep `WEBHOOK_SECRET` long and private; anyone with it can send your server orders.
- Never commit `.env` (it's git-ignored).
- Prefer allow-listing TradingView's webhook IPs at your reverse proxy.
- Start every live integration on a sandbox/testnet with the smallest possible size.
