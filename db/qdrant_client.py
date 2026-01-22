# db/qdrant_client.py
from qdrant_client import QdrantClient

# SINGLE shared client for the entire app
client = QdrantClient(path="qdrant_data")
