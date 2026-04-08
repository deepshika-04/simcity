"""
run.py — Digital Twin simulation engine entry point.

Usage:
    python run.py                     # uses EVENT from .env
    python run.py --event flood       # override event at runtime
    python run.py --event festival --interval 3
"""

import argparse
import logging
import time
import sys

from config import TICK_INTERVAL, ACTIVE_EVENT
from utils.db import setup_collections
from simulators import traffic_tick, hospital_tick, supply_tick

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("engine")

VALID_EVENTS = ["normal", "festival", "flood", "accident"]


def parse_args():
    parser = argparse.ArgumentParser(description="City Digital Twin Simulator")
    parser.add_argument(
        "--event", choices=VALID_EVENTS, default=ACTIVE_EVENT,
        help="Active event scenario",
    )
    parser.add_argument(
        "--interval", type=int, default=TICK_INTERVAL,
        help="Seconds between ticks",
    )
    return parser.parse_args()


def run_tick(event: str, tick_number: int):
    logger.info(f"── Tick {tick_number} | event={event} ──")
    try:
        t_docs = traffic_tick(event)
        h_docs = hospital_tick(event)
        s_docs = supply_tick(event)

        # Quick console summary
        avg_cong  = sum(d["congestion_pct"] for d in t_docs) / len(t_docs)
        avg_occ   = sum(d["occupancy_pct"]  for d in h_docs) / len(h_docs)
        avg_stock = sum(d["stock_pct"]       for d in s_docs) / len(s_docs)
        incidents = sum(1 for d in t_docs if d["incident"])

        logger.info(
            f"  traffic  → avg_cong={avg_cong:.1f}%  incidents={incidents}"
        )
        logger.info(
            f"  hospital → avg_occupancy={avg_occ:.1f}%"
        )
        logger.info(
            f"  supply   → avg_stock={avg_stock:.1f}%"
        )
    except Exception as exc:
        logger.error(f"Tick {tick_number} failed: {exc}", exc_info=True)


def main():
    args = parse_args()
    logger.info(f"Starting Digital Twin engine | event={args.event} | interval={args.interval}s")

    setup_collections()

    tick_number = 0
    try:
        while True:
            tick_number += 1
            run_tick(args.event, tick_number)
            time.sleep(args.interval)
    except KeyboardInterrupt:
        logger.info("Engine stopped by user.")
        sys.exit(0)


if __name__ == "__main__":
    main()