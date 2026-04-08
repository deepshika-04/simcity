from pymongo import MongoClient, ASCENDING
from pymongo.errors import CollectionInvalid
from config import MONGO_URI, DB_NAME
import logging

logger = logging.getLogger(__name__)

_client = None

def get_db():
    global _client
    if _client is None:
        _client = MongoClient(MONGO_URI)
    return _client[DB_NAME]


def setup_collections():
    """
    Create time-series collections and the alerts collection.
    Safe to call multiple times — skips if already exists.
    """
    db = get_db()

    ts_collections = [
        ("traffic_events",   "segment_id"),
        ("hospital_metrics", "ward_id"),
        ("supply_events",    "item_id"),
    ]

    for coll_name, meta_field in ts_collections:
        try:
            db.create_collection(
                coll_name,
                timeseries={
                    "timeField": "timestamp",
                    "metaField": meta_field,
                    "granularity": "seconds",
                },
            )
            logger.info(f"Created time-series collection: {coll_name}")
        except CollectionInvalid:
            logger.debug(f"Collection already exists: {coll_name}")

    # Alerts is a normal collection — no time-series needed
    if "alerts" not in db.list_collection_names():
        db.create_collection("alerts")
        db["alerts"].create_index([("timestamp", ASCENDING)])
        db["alerts"].create_index([("domain", ASCENDING), ("severity", ASCENDING)])
        logger.info("Created alerts collection with indexes")

    logger.info("MongoDB setup complete.")