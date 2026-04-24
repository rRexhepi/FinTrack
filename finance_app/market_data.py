"""yfinance wrapper with Django's cache in front.

Before this module, ``Investment.current_value`` and
``Investment.purchase_price_per_share`` called
``yf.Ticker(...).history(...)`` inside property access — so rendering a
list of N investments triggered 2N synchronous HTTP round-trips to
Yahoo on every request, and re-opening the dashboard one second later
did it all over again.

Centralising the fetch here lets us:

* cache current prices for a few minutes and historical prices for a
  day (historical data is, for our purposes, immutable);
* batch current-price lookups for a dashboard page with
  :func:`get_current_prices`, so the viewset can pass a pre-warmed
  ``{ticker: price}`` dict down through serializer context;
* keep the network boundary out of the model layer, where attribute
  access looks cheap but wasn't.
"""

from __future__ import annotations

import logging
from datetime import date, timedelta
from decimal import Decimal, InvalidOperation
from typing import Iterable

import yfinance as yf
from django.core.cache import cache

logger = logging.getLogger(__name__)

CURRENT_PRICE_TTL = 300  # 5 min — balance freshness against rate limits.
FAILURE_TTL = 60  # negative-cache a failed lookup so every dashboard
#                   page load doesn't eat another yfinance timeout per
#                   ticker when Yahoo's rate-limiting our IP.
HISTORICAL_PRICE_TTL = 24 * 60 * 60  # 24 hr — historical closes don't move.
_PRICE_WINDOW_DAYS = 5  # pad historical fetch to dodge market holidays.

# Sentinel that lets us distinguish "nothing cached yet" from "we cached
# a failure (None) last time" — `cache.get` returns None for both by
# default, which is the reason this module kept re-hitting yfinance.
_CACHE_MISS = object()


def _current_cache_key(ticker: str) -> str:
    return f"market:current:{ticker.upper()}"


def _historical_cache_key(ticker: str, d: date) -> str:
    return f"market:hist:{ticker.upper()}:{d.isoformat()}"


def _to_decimal(value) -> Decimal | None:
    try:
        result = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        return None
    # yfinance returns NaN for missing closes; Decimal('NaN') parses fine
    # but arithmetic on it blows up downstream.
    if result.is_nan():
        return None
    return result


def get_current_price(ticker: str) -> Decimal | None:
    """Latest close price for ``ticker``; ``None`` if unavailable."""
    if not ticker:
        return None
    key = _current_cache_key(ticker)
    cached = cache.get(key, _CACHE_MISS)
    if cached is not _CACHE_MISS:
        return cached
    try:
        df = yf.Ticker(ticker).history(period="1d")
    except Exception as exc:
        logger.warning("yfinance current_price failed for %s: %s", ticker, exc)
        cache.set(key, None, FAILURE_TTL)
        return None
    if df.empty:
        cache.set(key, None, FAILURE_TTL)
        return None
    price = _to_decimal(df["Close"].iloc[-1])
    if price is None:
        cache.set(key, None, FAILURE_TTL)
        return None
    cache.set(key, price, CURRENT_PRICE_TTL)
    return price


def get_current_prices(tickers: Iterable[str]) -> dict[str, Decimal]:
    """Best-effort ``{ticker: latest_close}`` map for a batch.

    Tickers that fail to resolve are dropped silently — the caller
    decides how to present a missing price to the user.
    """
    out: dict[str, Decimal] = {}
    for ticker in {t.upper() for t in tickers if t}:
        price = get_current_price(ticker)
        if price is not None:
            out[ticker] = price
    return out


def get_price_on_date(ticker: str, target: date) -> Decimal | None:
    """Close price for ``ticker`` on ``target`` (or the nearest earlier day).

    ``yfinance`` returns an empty frame when ``start == end`` falls on a
    market holiday, so we pull a ``_PRICE_WINDOW_DAYS`` window around
    the target and take the latest close on or before ``target``.
    """
    if not ticker or target is None:
        return None
    key = _historical_cache_key(ticker, target)
    cached = cache.get(key, _CACHE_MISS)
    if cached is not _CACHE_MISS:
        return cached
    start = target - timedelta(days=_PRICE_WINDOW_DAYS)
    end = target + timedelta(days=_PRICE_WINDOW_DAYS)
    try:
        df = yf.Ticker(ticker).history(start=start, end=end)
    except Exception as exc:
        logger.warning(
            "yfinance historical failed for %s on %s: %s", ticker, target, exc
        )
        cache.set(key, None, FAILURE_TTL)
        return None
    if df.empty:
        cache.set(key, None, FAILURE_TTL)
        return None
    on_or_before = df[df.index.date <= target]
    row = on_or_before if not on_or_before.empty else df
    price = _to_decimal(row["Close"].iloc[-1])
    if price is None:
        cache.set(key, None, FAILURE_TTL)
        return None
    cache.set(key, price, HISTORICAL_PRICE_TTL)
    return price
