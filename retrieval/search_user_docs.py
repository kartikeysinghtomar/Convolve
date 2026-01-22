from sentence_transformers import SentenceTransformer
from db.qdrant_client import client

# -----------------------------
# CONFIG
# -----------------------------
EMBED_MODEL = "sentence-transformers/all-mpnet-base-v2"

model = SentenceTransformer(EMBED_MODEL)


# -----------------------------
# INTERACTIVE DOC SEARCH
# -----------------------------
def search_user_docs(session_id: str, query: str, limit: int = 5):
    """
    Prints relevant chunks from user-uploaded PDFs / images.
    Used for interactive 'docs' command.
    """
    collection = f"user_docs_{session_id}"

    try:
        client.get_collection(collection)
    except Exception:
        print("No user-uploaded documents found.")
        return

    query_vector = model.encode(query).tolist()

    results = client.search(
        collection_name=collection,
        query_vector=query_vector,
        limit=limit
    )

    if not results:
        print("No relevant information found in uploaded documents.")
        return

    print("\nFrom your uploaded documents:\n")

    for r in results:
        payload = r.payload or {}

        file_type = payload.get("file_type", "unknown")
        file_name = payload.get("file_name", "")
        text = payload.get("text", "")

        print(f"• {file_type.upper()} | {file_name}")
        print(text[:300].strip())
        print("-" * 50)


# -----------------------------
# CONTEXT RETRIEVAL FOR SCHEMES
# -----------------------------
def get_user_doc_context(session_id: str, query: str, limit: int = 3) -> str:
    """
    Returns concatenated text from user-uploaded docs.
    Used to influence scheme retrieval.
    """
    collection = f"user_docs_{session_id}"

    try:
        client.get_collection(collection)
    except Exception:
        return ""

    query_vector = model.encode(query).tolist()

    results = client.search(
        collection_name=collection,
        query_vector=query_vector,
        limit=limit
    )

    texts = []
    for r in results:
        payload = r.payload or {}
        text = payload.get("text")
        if text:
            texts.append(text)

    return " ".join(texts)
