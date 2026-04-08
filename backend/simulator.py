import time
import random
import requests
from datetime import datetime, timezone

# Configuration
INGEST_URL = "http://localhost:8000/ingest"

# Define exactly 10 nodes (5 hospitals, 5 traffic signals) with fixed lat/lng
NODES = [
    {"id": 1, "type": "hospital", "lat": 40.7128, "lng": -74.0060},
    {"id": 2, "type": "hospital", "lat": 40.7138, "lng": -74.0070},
    {"id": 3, "type": "hospital", "lat": 40.7148, "lng": -74.0080},
    {"id": 4, "type": "hospital", "lat": 40.7158, "lng": -74.0090},
    {"id": 5, "type": "hospital", "lat": 40.7168, "lng": -74.0100},
    {"id": 6, "type": "traffic", "lat": 40.7589, "lng": -73.9851},
    {"id": 7, "type": "traffic", "lat": 40.7599, "lng": -73.9861},
    {"id": 8, "type": "traffic", "lat": 40.7609, "lng": -73.9871},
    {"id": 9, "type": "traffic", "lat": 40.7619, "lng": -73.9881},
    {"id": 10, "type": "traffic", "lat": 40.7629, "lng": -73.9891},
]

# Track the current state for each node
state = {}
for node in NODES:
    state[node["id"]] = {
        "water_level": 0,
        "power": 100
    }

def get_status(water_level):
    """Determine status based on water level thresholds"""
    if water_level > 70:
        return "CRITICAL"
    elif water_level > 40:
        return "WARNING"
    return "NORMAL"

def simulate_step():
    """Run one tick of the simulation for all nodes"""
    for node in NODES:
        node_id = node["id"]
        node_type = node["type"]
        current_state = state[node_id]
        
        # 1. Gradually increase water level
        water_increase = random.randint(1, 4)
        current_state["water_level"] = min(100, current_state["water_level"] + water_increase)
        
        water_level = current_state["water_level"]
        status = get_status(water_level)
        
        # 2. Power decreases as water increases
        power_loss = random.randint(0, 2)
        if water_level > 40:
            power_loss += random.randint(1, 3)
            
        # 3. Hospitals: when CRITICAL → power drops faster
        if status == "CRITICAL" and node_type == "hospital":
            power_loss += random.randint(2, 6)
            
        current_state["power"] = max(0, current_state["power"] - power_loss)
        
        # Prepare HTTP payload
        payload = {
            "id": node_id,
            "type": node_type,
            "lat": node["lat"],
            "lng": node["lng"],
            "water_level": current_state["water_level"],
            "power": current_state["power"],
            "status": status,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        # Send data to ingest endpoint
        try:
            response = requests.post(INGEST_URL, json=payload, timeout=2)
            if response.status_code == 201:
                print(f"[{status}] Sent data for Node {node_id} ({node_type}) - Water: {water_level}%, Power: {current_state['power']}%")
            else:
                print(f"Failed to send data for Node {node_id}: {response.status_code} - {response.text}")
        except requests.exceptions.RequestException as e:
            print(f"Connection error when sending data for Node {node_id}: Endpoint might not be running.")

if __name__ == "__main__":
    print("Starting SimCity disaster simulator...")
    print(f"Targeting ingest URL: {INGEST_URL}")
    while True:
        simulate_step()
        print("--- Simulation step complete. Waiting 2 seconds... ---")
        time.sleep(2)
