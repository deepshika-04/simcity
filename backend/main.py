from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timezone
import logging
from models import NodeBase, NodeResponse
from database import nodes_collection

app = FastAPI(title="SimCity API")

# Setup CORS to allow all origins for now
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "SimCity API running"}

@app.post("/ingest", status_code=status.HTTP_201_CREATED)
def ingest_data(node: NodeBase):
    if nodes_collection is None:
        raise HTTPException(status_code=500, detail="Database connection not available")

    # Dump pydantic model to dict
    node_dict = node.model_dump()
    
    # Add server-side timestamp if missing
    if node_dict.get("timestamp") is None:
        node_dict["timestamp"] = datetime.now(timezone.utc)
        
    try:
        # Insert into MongoDB
        nodes_collection.insert_one(node_dict)
        return {"message": "Node data ingested successfully"}
    except Exception as e:
        logging.error(f"Error during ingestion: {e}")
        raise HTTPException(status_code=500, detail="Internal server error while saving data")

@app.get("/city-status", response_model=dict)
def get_city_status():
    if nodes_collection is None:
        raise HTTPException(status_code=500, detail="Database connection not available")

    try:
        # Aggregate pipeline to group by 'id' and find the record with the most recent 'timestamp'
        pipeline = [
            {"$sort": {"timestamp": -1}},
            {"$group": {
                "_id": "$id",
                "latest_data": {"$first": "$$ROOT"}
            }},
            {"$replaceRoot": {"newRoot": "$latest_data"}},
            {"$project": {"_id": 0}} # Exclude the Mongo internal _id field
        ]
        
        latest_nodes = list(nodes_collection.aggregate(pipeline))
        return {"nodes": latest_nodes}
    except Exception as e:
        logging.error(f"Error fetching city status: {e}")
        raise HTTPException(status_code=500, detail="Internal server error while retrieving data")
