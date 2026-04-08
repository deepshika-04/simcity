from datetime import datetime, timezone
from config import ALERT_THRESHOLDS
from utils.db import get_db
import logging

logger = logging.getLogger(__name__)


def _write_alert(domain: str, entity_id: str, metric: str,
                  value: float, threshold: float, severity: str, event: str):
    db = get_db()
    alert = {
        "timestamp":  datetime.now(timezone.utc),
        "domain":     domain,
        "entity_id":  entity_id,
        "metric":     metric,
        "value":      round(value, 2),
        "threshold":  threshold,
        "severity":   severity,
        "event":      event,
        "resolved":   False,
    }
    db["alerts"].insert_one(alert)
    logger.warning(f"ALERT [{severity.upper()}] {domain}/{entity_id} — "
                   f"{metric}={value:.1f} (threshold={threshold})")


def check_traffic_alerts(doc: dict, event: str):
    cong = doc.get("congestion_pct", 0)
    score = doc.get("flow_score", 100)
    seg = doc.get("segment_id", "unknown")

    if cong >= ALERT_THRESHOLDS["traffic_congestion_pct"]:
        severity = "critical" if cong >= 90 else "warning"
        _write_alert("traffic", seg, "congestion_pct", cong,
                     ALERT_THRESHOLDS["traffic_congestion_pct"], severity, event)

    if score <= ALERT_THRESHOLDS["traffic_flow_score"]:
        _write_alert("traffic", seg, "flow_score", score,
                     ALERT_THRESHOLDS["traffic_flow_score"], "warning", event)


def check_hospital_alerts(doc: dict, event: str):
    occ = doc.get("occupancy_pct", 0)
    ward = doc.get("ward_id", "unknown")

    if occ >= ALERT_THRESHOLDS["hospital_occupancy_pct"]:
        severity = "critical" if occ >= 95 else "warning"
        _write_alert("hospital", ward, "occupancy_pct", occ,
                     ALERT_THRESHOLDS["hospital_occupancy_pct"], severity, event)


def check_supply_alerts(doc: dict, event: str):
    stock_pct = doc.get("stock_pct", 100)
    item = doc.get("item_id", "unknown")

    if stock_pct <= ALERT_THRESHOLDS["supply_stock_pct"]:
        severity = "critical" if stock_pct <= 10 else "warning"
        _write_alert("supply", item, "stock_pct", stock_pct,
                     ALERT_THRESHOLDS["supply_stock_pct"], severity, event)