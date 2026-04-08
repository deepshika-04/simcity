import os
import logging
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
client = None
db = None
nodes_collection = None

# Configure logging
logging.basicConfig(level=logging.INFO)

try:
    # Connect to MongoDB
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    
    # Trigger a connection test
    client.admin.command('ping')
    logging.info("Connected to MongoDB successfully.")
    
    # Create / Use the "simcity" database
    db = client["simcity"]
    
    # Create / Use the "nodes" collection
    nodes_collection = db["nodes"]
    
    # Add indexing on "id" and "timestamp" for efficient retrieval
    nodes_collection.create_index([("id", 1), ("timestamp", -1)])
    logging.info("Indexes confirmed on nodes collection.")
    
except ConnectionFailure:
    logging.error("Failed to connect to MongoDB. Please make sure MongoDB is running and MONGO_URI is correct.")
except Exception as e:
    logging.error(f"An error occurred while connecting to MongoDB: {e}")
