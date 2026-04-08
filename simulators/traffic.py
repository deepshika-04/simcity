"""
Traffic simulator.

Each tick generates one document per road segment:
  - speed_kmh         : avg vehicle speed after applying event multiplier
  - congestion_pct    : % of road capacity in use (capped at 100)
  - incident          : bool — random accident/blockage
  - flow_score        : derived 0-100 health metric
  - vehicles_per_hour : estimated throughput
"""

import random
from datetime import datetime, timezone
from config import ROAD_SEGMENTS, EVENT_MULTIPLIERS
from utils.db import get_db
from utils.alerts import check_traffic_alerts
import logging

logger = logging.getLogger(__name__)

# Baseline ranges (normal conditions, no event)
_BASE_SPEED_KMH   = (40, 65)
_BASE_CONG_PCT    = (10, 45)
_BASE_VPH         = (800, 1400)   # vehicles per hour


def _flow_score(congestion_pct: float, incident: bool) -> float:
    """Higher is better. Drops with congestion and incidents."""
    score = 100 - (congestion_pct * 0.6) - (15 if incident else 0)
    return round(max(0.0, min(100.0, score)), 1)


def simulate_tick(event: str = "normal") -> list[dict]:
    """
    Generate one reading per road segment and persist to MongoDB.
    Returns the list of documents inserted.
    """
    db   = get_db()
    mults = EVENT_MULTIPLIERS[event]["traffic"]
    docs  = []

    for seg in ROAD_SEGMENTS:
        base_speed = random.uniform(*_BASE_SPEED_KMH)
        base_cong  = random.uniform(*_BASE_CONG_PCT)
        base_vph   = random.uniform(*_BASE_VPH)

        speed    = round(base_speed * mults["speed_mult"], 1)
        cong     = round(min(base_cong * mults["cong_mult"], 100.0), 1)
        incident = random.random() < mults["inc_prob"]
        vph      = round(base_vph * mults["speed_mult"])

        doc = {
            "timestamp":        datetime.now(timezone.utc),
            "segment_id":       seg["id"],
            "segment_name":     seg["name"],
            "speed_kmh":        speed,
            "congestion_pct":   cong,
            "vehicles_per_hour": vph,
            "incident":         incident,
            "flow_score":       _flow_score(cong, incident),
            "event":            event,
        }

        db["traffic_events"].insert_one(doc)
        check_traffic_alerts(doc, event)
        docs.append(doc)
        logger.debug(f"traffic | {seg['name']} | spd={speed} cong={cong}% inc={incident}")

    return docs