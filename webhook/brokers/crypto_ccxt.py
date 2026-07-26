"""Crypto execution via ccxt (optional).

Supports any ccxt exchange (Binance, Bybit, Kraken, ...). Configure through env:

    BROKER=crypto
    LIVE_TRADING=true
    CCXT_EXCHANGE=binance
    CCXT_API_KEY=...
    CCXT_SECRET=...
    CCXT_SANDBOX=true            # use the exchange testnet first!
    ORDER_QUOTE_AMOUNT=25        # quote-currency size per trade, e.g. 25 USDT

Start on the exchange TESTNET (CCXT_SANDBOX=true) and with tiny size. This adapter
places a market order in the signal direction and, when the exchange supports it,
attaches stop-loss / take-profit. Treat it as a starting point you must review.
"""
from __future__ import annotations

import os
from typing import Any


class CcxtBroker:
    name = "crypto"

    def __init__(self) -> None:
        try:
            import ccxt  # noqa: F401
        except ImportError as exc:  # pragma: no cover
            raise RuntimeError("ccxt is not installed. Run: pip install ccxt") from exc
        import ccxt

        exch_id = os.getenv("CCXT_EXCHANGE", "binance")
        if not hasattr(ccxt, exch_id):
            raise ValueError(f"Unknown ccxt exchange {exch_id!r}")
        klass = getattr(ccxt, exch_id)
        self.exchange = klass(
            {
                "apiKey": os.getenv("CCXT_API_KEY", ""),
                "secret": os.getenv("CCXT_SECRET", ""),
                "enableRateLimit": True,
            }
        )
        if os.getenv("CCXT_SANDBOX", "true").lower() == "true":
            try:
                self.exchange.set_sandbox_mode(True)
            except Exception:
                pass  # some exchanges have no sandbox
        self.quote_amount = float(os.getenv("ORDER_QUOTE_AMOUNT", "25"))

    def _symbol(self, ticker: str) -> str:
        """Best-effort map a TradingView ticker (e.g. BINANCE:BTCUSDT) to ccxt (BTC/USDT)."""
        t = ticker.split(":")[-1].upper()
        for quote in ("USDT", "USDC", "USD", "BTC", "ETH"):
            if t.endswith(quote) and len(t) > len(quote):
                return f"{t[:-len(quote)]}/{quote}"
        return t

    def execute(self, signal: dict[str, Any]) -> dict[str, Any]:
        action = signal["action"]
        symbol = self._symbol(signal["ticker"])

        if action == "close":
            # Flatten the position if the exchange/account supports it.
            try:
                self.exchange.cancel_all_orders(symbol)
            except Exception:
                pass
            return {"broker": self.name, "symbol": symbol, "action": "close", "note": "orders cancelled"}

        side = "buy" if action == "buy" else "sell"
        price = signal.get("price")
        # Convert quote size -> base amount using the signal price (fallback to ticker price).
        if not price:
            price = self.exchange.fetch_ticker(symbol)["last"]
        amount = self.quote_amount / float(price)
        amount = float(self.exchange.amount_to_precision(symbol, amount))

        order = self.exchange.create_order(symbol, "market", side, amount)

        attached: dict[str, Any] = {}
        sl, tp = signal.get("sl"), signal.get("tp")
        exit_side = "sell" if side == "buy" else "buy"
        try:
            if sl:
                attached["sl"] = self.exchange.create_order(
                    symbol, "stop", exit_side, amount, None, {"stopPrice": sl, "reduceOnly": True}
                )
            if tp:
                attached["tp"] = self.exchange.create_order(
                    symbol, "limit", exit_side, amount, tp, {"reduceOnly": True}
                )
        except Exception as exc:  # exchange may not support these order types
            attached["exit_orders_error"] = str(exc)

        return {
            "broker": self.name,
            "symbol": symbol,
            "side": side,
            "amount": amount,
            "entry_order_id": order.get("id"),
            "attached": attached,
        }
