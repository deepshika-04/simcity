"""
Supply chain simulator.

Maintains a simple stateful inventory that drains each tick and
replenishes partially based on delivery_eta.

Each tick document contains:
  - stock_units       : current inventory level
  - stock_pct         : stock / max_stock * 100
  - units_consumed    : consumed this tick
  - delivery_eta_hours: estimated hours until next delivery
  - delivery_delayed  : bool — delivery disrupted by event
"""

import random
from datetime import datetime, timezone
from config import SUPPLY_ITEMS, EVENT_MULTIPLIERS
from utils.db import get_db
from utils.alerts import check_supply_alerts
import logging

logger = logging.getLogger(__name__)

# Stateful inventory — initialise at 80% capacity
_inventory: dict[str, float] = {}

_BASE_DRAIN_RATE   = (0.02, 0.06)   # fraction of max_stock consumed per tick
_BASE_RESTOCK_RATE = (0.03, 0.08)   # fraction restocked if delivery arrives
_BASE_ETA_HOURS    = (2, 12)


def _init_inventory():
    for item in SUPPLY_ITEMS:
        if item["id"] not in _inventory:
            _inventory[item["id"]] = item["max_stock"] * 0.80


def simulate_tick(event: str = "normal") -> list[dict]:
    _init_inventory()
    db    = get_db()
    mults = EVENT_MULTIPLIERS[event]["supply"]
    docs  = []

    for item in SUPPLY_ITEMS:
        iid      = item["id"]
        max_stk  = item["max_stock"]
        cur_stk  = _inventory[iid]

        # Consumption
        drain_frac  = random.uniform(*_BASE_DRAIN_RATE) * mults["drain_mult"]
        consumed    = round(min(cur_stk, max_stk * drain_frac), 2)
        cur_stk    -= consumed

        # Replenishment
        delivery_delayed = random.random() < (mults["delay_mult"] * 0.08)
        if not delivery_delayed:
            restock_frac = random.uniform(*_BASE_RESTOCK_RATE)
            cur_stk = min(max_stk, cur_stk + max_stk * restock_frac)

        # ETA
        eta = round(random.uniform(*_BASE_ETA_HOURS) * mults["delay_mult"], 1)

        cur_stk = max(0.0, cur_stk)
        _inventory[iid] = cur_stk

        doc = {
            "timestamp":          datetime.now(timezone.utc),
            "item_id":            iid,
            "item_name":          item["name"],
            "unit":               item["unit"],
            "max_stock":          max_stk,
            "stock_units":        round(cur_stk, 2),
            "stock_pct":          round((cur_stk / max_stk) * 100, 1),
            "units_consumed":     consumed,
            "delivery_eta_hours": eta,
            "delivery_delayed":   delivery_delayed,
            "event":              event,
        }

        db["supply_events"].insert_one(doc)
        check_supply_alerts(doc, event)
        docs.append(doc)
        logger.debug(f"supply | {item['name']} | stock={doc['stock_pct']}% delayed={delivery_delayed}")

    return docs