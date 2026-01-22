import pandas as pd
import uuid
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct

CSV_PATH = "data/schemes.csv"
COLLECTION_NAME = "schemes_index"
MODEL_NAME = "sentence-transformers/all-mpnet-base-v2"
VECTOR_SIZE = 768
BATCH_SIZE = 20  # SMALL on Windows

from db.qdrant_client import client


model = SentenceTransformer(MODEL_NAME)


def ensure_collection():
    collections = client.get_collections().collections
    if any(c.name == COLLECTION_NAME for c in collections):
        return

    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(
            size=VECTOR_SIZE,
            distance=Distance.COSINE
        )
    )


def ingest():
    print("Loading CSV...")
    df = pd.read_csv(CSV_PATH)

    ensure_collection()

    buffer = []
    total = 0

    for _, row in df.iterrows():
        text = f"""
        {row.get('scheme_name','')}
        {row.get('schemeCategory','')}
        {row.get('eligibility','')}
        {row.get('benefits','')}
        """

        vector = model.encode(text).tolist()

        payload = {
            "scheme_name": row.get("scheme_name", ""),
            "schemeCategory": row.get("schemeCategory", ""),
            "eligibility": row.get("eligibility", ""),
            "benefits": row.get("benefits", ""),
            "application": row.get("application", ""),
            "documents": row.get("documents", ""),
            "valid_states": row.get("valid_states", "")
        }

        buffer.append(
            PointStruct(
                id=str(uuid.uuid4()),
                vector=vector,
                payload=payload
            )
        )

        if len(buffer) >= BATCH_SIZE:
            client.upsert(COLLECTION_NAME, buffer)
            total += len(buffer)
            print(f"Ingested {total} schemes...")
            buffer.clear()

    if buffer:
        client.upsert(COLLECTION_NAME, buffer)
        total += len(buffer)

    print(f"✅ Ingestion complete: {total} schemes.")


if __name__ == "__main__":
    ingest()
