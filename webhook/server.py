"""
ICC-OTE webhook bridge
======================

Receives TradingView alerts (JSON) from the ICC + OTE Pine strategy/indicator
and routes them to a broker adapter.

SAFETY FIRST
------------
* Runs in **paper mode** by default — every signal is logged, nothing is traded.
* Live execution requires BOTH:  LIVE_TRADING=true  AND a configured broker.
* Every request must carry the shared secret (?secret= or "secret" in the body)
  that matches WEBHOOK_SECRET, otherwise it is rejected.

Run it:
    pip install -r requirements.txt
    cp .env.example .env          # then edit .env
    uvicorn server:app --host 0.0.0.0 --port 8000

Point your TradingView alert webhook URL at:
    https://<your-host>/webhook?secret=<WEBHOOK_SECRET>
"""
from __future__ import annotations

import json
import logging
import os
from datetime import datetime, timezone
from typing import Any

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request

from brokers import get_broker

load_dotenv()

LOG_FILE = os.getenv("SIGNAL_LOG", "signals.log")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)s  %(message)s",
    handlers=[logging.FileHandler(LOG_FILE), logging.StreamHandler()],
)
log = logging.getLogger("icc-ote")

WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "")
LIVE_TRADING = os.getenv("LIVE_TRADING", "false").lower() == "true"

app = FastAPI(title="ICC-OTE Webhook Bridge", version="1.0.0")
broker = get_broker(os.getenv("BROKER", "paper"))

VALID_ACTIONS = {"buy", "sell", "close"}


def _check_secret(request: Request, body: dict[str, Any]) -> None:
    """Reject the request unless the shared secret matches."""
    if not WEBHOOK_SECRET:
        raise HTTPException(500, "Server misconfigured: WEBHOOK_SECRET is not set.")
    supplied = request.query_params.get("secret") or body.get("secret")
    if supplied != WEBHOOK_SECRET:
        raise HTTPException(401, "Invalid or missing secret.")


async def _parse_body(request: Request) -> dict[str, Any]:
    """Accept both JSON and raw-text alert bodies from TradingView."""
    raw = (await request.body()).decode("utf-8", errors="replace").strip()
    if not raw:
        raise HTTPException(400, "Empty request body.")
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        raise HTTPException(400, f"Body is not valid JSON: {raw[:200]!r}")


@app.get("/")
def health() -> dict[str, Any]:
    return {
        "service": "icc-ote-webhook",
        "status": "ok",
        "live_trading": LIVE_TRADING,
        "broker": broker.name,
        "time": datetime.now(timezone.utc).isoformat(),
    }


@app.post("/webhook")
async def webhook(request: Request) -> dict[str, Any]:
    body = await _parse_body(request)
    _check_secret(request, body)

    action = str(body.get("action", "")).lower()
    ticker = str(body.get("ticker", "")).strip()
    if action not in VALID_ACTIONS:
        raise HTTPException(400, f"Unknown action {action!r}; expected one of {sorted(VALID_ACTIONS)}.")
    if not ticker:
        raise HTTPException(400, "Missing 'ticker'.")

    signal = {
        "ticker": ticker,
        "action": action,
        "price": body.get("price"),
        "sl": body.get("sl"),
        "tp": body.get("tp"),
        "tf": body.get("tf"),
        "strategy": body.get("strategy", "ICC-OTE"),
        "received_at": datetime.now(timezone.utc).isoformat(),
    }
    log.info("SIGNAL %s", json.dumps(signal))

    if not LIVE_TRADING:
        log.info("PAPER MODE — not executing. Set LIVE_TRADING=true to go live.")
        return {"status": "logged", "live": False, "signal": signal}

    try:
        result = broker.execute(signal)
    except Exception as exc:  # broker adapters should raise on failure
        log.exception("Broker execution failed")
        raise HTTPException(502, f"Broker execution failed: {exc}")

    log.info("EXECUTED %s", json.dumps(result))
    return {"status": "executed", "live": True, "signal": signal, "result": result}
