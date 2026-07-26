"""Paper broker — the safe default. Records intent, never touches a real account."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


class PaperBroker:
    name = "paper"

    def execute(self, signal: dict[str, Any]) -> dict[str, Any]:
        return {
            "broker": self.name,
            "filled": False,
            "note": "paper trade — no real order placed",
            "would_have": {
                "action": signal.get("action"),
                "ticker": signal.get("ticker"),
                "price": signal.get("price"),
                "sl": signal.get("sl"),
                "tp": signal.get("tp"),
            },
            "at": datetime.now(timezone.utc).isoformat(),
        }
