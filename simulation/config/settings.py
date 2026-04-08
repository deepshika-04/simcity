import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME   = os.getenv("DB_NAME", "city_twin")
TICK_INTERVAL = int(os.getenv("TICK_INTERVAL_SECONDS", 5))
ACTIVE_EVENT  = os.getenv("EVENT", "normal")

# ── Road segments ────────────────────────────────────────────────
ROAD_SEGMENTS = [
    {"id": "nh65_west",   "name": "NH-65 West",    "length_km": 12},
    {"id": "nh65_east",   "name": "NH-65 East",    "length_km": 10},
    {"id": "ring_road",   "name": "Ring Road",     "length_km": 8},
    {"id": "outer_ring",  "name": "Outer Ring",    "length_km": 15},
    {"id": "ns_arterial", "name": "N-S Arterial",  "length_km": 6},
    {"id": "e_connector", "name": "E Connector",   "length_km": 5},
]

# ── Hospital wards ───────────────────────────────────────────────
HOSPITAL_WARDS = [
    {"id": "general",    "name": "General Ward",      "total_beds": 120},
    {"id": "icu",        "name": "ICU",               "total_beds": 30},
    {"id": "emergency",  "name": "Emergency",         "total_beds": 50},
    {"id": "pediatric",  "name": "Pediatric",         "total_beds": 40},
]

# ── Supply chain items ───────────────────────────────────────────
SUPPLY_ITEMS = [
    {"id": "rice",       "name": "Rice",           "unit": "tonnes",  "max_stock": 500},
    {"id": "fuel",       "name": "Fuel",           "unit": "kilolitres", "max_stock": 200},
    {"id": "medicine",   "name": "Medicine kits",  "unit": "units",   "max_stock": 1000},
    {"id": "water",      "name": "Bottled water",  "unit": "pallets", "max_stock": 300},
]

# ── Event multiplier table ───────────────────────────────────────
EVENT_MULTIPLIERS = {
    "normal": {
        "traffic": {"speed_mult": 1.0,  "cong_mult": 1.0,  "inc_prob": 0.05},
        "hospital":{"occupancy_mult": 1.0, "er_surge_prob": 0.05},
        "supply":  {"drain_mult": 1.0,  "delay_mult": 1.0},
    },
    "festival": {
        "traffic": {"speed_mult": 0.6,  "cong_mult": 2.2,  "inc_prob": 0.10},
        "hospital":{"occupancy_mult": 1.3, "er_surge_prob": 0.15},
        "supply":  {"drain_mult": 1.8,  "delay_mult": 1.2},
    },
    "flood": {
        "traffic": {"speed_mult": 0.25, "cong_mult": 3.8,  "inc_prob": 0.35},
        "hospital":{"occupancy_mult": 2.5, "er_surge_prob": 0.50},
        "supply":  {"drain_mult": 3.0,  "delay_mult": 4.0},
    },
    "accident": {
        "traffic": {"speed_mult": 0.45, "cong_mult": 2.1,  "inc_prob": 0.55},
        "hospital":{"occupancy_mult": 1.8, "er_surge_prob": 0.40},
        "supply":  {"drain_mult": 1.2,  "delay_mult": 1.5},
    },
}

# ── Alert thresholds ─────────────────────────────────────────────
ALERT_THRESHOLDS = {
    "traffic_congestion_pct": 70,
    "hospital_occupancy_pct": 85,
    "supply_stock_pct":       20,   # alert when stock drops below 20%
    "traffic_flow_score":     40,   # alert when score drops below 40
}