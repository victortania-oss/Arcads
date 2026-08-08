"""Broker adapter registry.

Adapters implement a single method, ``execute(signal) -> dict``. The default is
the paper adapter, which never places a real order. Add live adapters here as you
wire up real execution.
"""
from __future__ import annotations

from .base import Broker
from .paper import PaperBroker


def get_broker(name: str) -> Broker:
    name = (name or "paper").lower()
    if name == "paper":
        return PaperBroker()
    if name == "crypto":
        # Imported lazily so ccxt is only required when actually trading crypto.
        from .crypto_ccxt import CcxtBroker

        return CcxtBroker()
    raise ValueError(
        f"Unknown broker {name!r}. Options: 'paper', 'crypto'. "
        "Futures (MNQ/MES) need a third-party bridge — see docs/SETUP.md."
    )
