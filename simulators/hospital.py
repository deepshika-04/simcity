"""
Hospital simulator.

Each tick generates one document per ward:
  - occupied_beds     : current beds in use
  - occupancy_pct     : occupied / total * 100
  - er_wait_minutes   : estimated ER wait time
  - er_surge          : bool — sudden surge event
  - available_beds    : total - occupied
"""

import random
from datetime import datetime, timezone
from config import HOSPITAL_WARDS, EVENT_MULTIPLIERS
from utils.db import get_db
from utils.alerts import check_hospital_alerts
import logging

logger = logging.getLogger(__name__)

# Baseline occupancy range (fraction of total beds, normal conditions)
_BASE_OCCUPANCY_FRACTION = (0.55, 0.75)
_BASE_ER_WAIT_MIN        = (10, 35)


def simulate_tick(event: str = "normal") -> list[dict]:
    db    = get_db()
    mults = EVENT_MULTIPLIERS[event]["hospital"]
    docs  = []

    for ward in HOSPITAL_WARDS:
        base_occ_frac = random.uniform(*_BASE_OCCUPANCY_FRACTION)
        base_er_wait  = random.uniform(*_BASE_ER_WAIT_MIN)

        raw_occ_frac  = base_occ_frac * mults["occupancy_mult"]
        occ_frac      = min(raw_occ_frac, 1.0)           # cap at 100%
        occupied_beds = round(ward["total_beds"] * occ_frac)
        occupancy_pct = round(occ_frac * 100, 1)
        er_surge      = random.random() < mults["er_surge_prob"]
        er_wait       = round(base_er_wait * mults["occupancy_mult"]
                              * (1.5 if er_surge else 1.0), 1)

        doc = {
            "timestamp":      datetime.now(timezone.utc),
            "ward_id":        ward["id"],
            "ward_name":      ward["name"],
            "total_beds":     ward["total_beds"],
            "occupied_beds":  occupied_beds,
            "available_beds": ward["total_beds"] - occupied_beds,
            "occupancy_pct":  occupancy_pct,
            "er_wait_minutes": er_wait,
            "er_surge":       er_surge,
            "event":          event,
        }

        db["hospital_metrics"].insert_one(doc)
        check_hospital_alerts(doc, event)
        docs.append(doc)
        logger.debug(f"hospital | {ward['name']} | occ={occupancy_pct}% surge={er_surge}")

    return docs