from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
from db.qdrant_client import client

COLLECTION_NAME = "schemes_docs_index"
EMBEDDING_MODEL = "sentence-transformers/all-mpnet-base-v2"
model = SentenceTransformer(EMBEDDING_MODEL)


def search_documents(query, limit=5):
    query_vector = model.encode(query).tolist()

    results = client.search(
        collection_name=COLLECTION_NAME,
        query_vector=query_vector,
        limit=limit
    )

    if not results:
        print("\nNo supporting documents found.\n")
        return

    print("\nOfficial document references:\n")

    for r in results:
        p = r.payload
        print(f"• {p['scheme_name']} (PDF, page {p['page_number']})")
        print(f"  Excerpt: {p['text'][:300]}...\n")
