"""Broker adapter interface."""
from __future__ import annotations

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class Broker(Protocol):
    name: str

    def execute(self, signal: dict[str, Any]) -> dict[str, Any]:
        """Place / manage an order for the given signal.

        ``signal`` keys: ticker, action ('buy'|'sell'|'close'), price, sl, tp, tf.
        Return a JSON-serialisable dict describing what happened. Raise on failure.
        """
        ...
