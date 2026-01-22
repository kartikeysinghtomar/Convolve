import os
import uuid
from pathlib import Path
from db.qdrant_client import client

import fitz  # PyMuPDF
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, VectorParams, Distance

# ---------------- CONFIG ----------------

PDF_DIR = "data/pdfs"
COLLECTION_NAME = "schemes_docs_index"
EMBEDDING_MODEL = "sentence-transformers/all-mpnet-base-v2"
VECTOR_SIZE = 768
CHUNK_SIZE = 800  # characters

# ----------------------------------------

model = SentenceTransformer(EMBEDDING_MODEL)


def recreate_collection():
    try:
        client.delete_collection(COLLECTION_NAME)
        print("Old PDF collection deleted.")
    except Exception:
        pass

    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(
            size=VECTOR_SIZE,
            distance=Distance.COSINE
        )
    )
    print("PDF collection created.")


def chunk_text(text, size=CHUNK_SIZE):
    return [text[i:i + size] for i in range(0, len(text), size)]


def ingest():
    recreate_collection()

    pdf_files = list(Path(PDF_DIR).glob("*.pdf"))
    if not pdf_files:
        print("No PDFs found.")
        return

    total_chunks = 0

    for pdf_path in pdf_files:
        doc = fitz.open(pdf_path)
        scheme_name = pdf_path.stem.replace("_", " ").title()

        print(f"Ingesting {pdf_path.name}...")

        for page_number, page in enumerate(doc, start=1):
            text = page.get_text().strip()
            if not text:
                continue

            chunks = chunk_text(text)

            for chunk in chunks:
                vector = model.encode(chunk).tolist()

                payload = {
                    "scheme_name": scheme_name,
                    "source": "pdf",
                    "document_type": "guidelines",
                    "page_number": page_number,
                    "text": chunk
                }

                point = PointStruct(
                    id=str(uuid.uuid4()),
                    vector=vector,
                    payload=payload
                )

                client.upsert(
                    collection_name=COLLECTION_NAME,
                    points=[point]
                )

                total_chunks += 1

    print(f"PDF ingestion complete. Total chunks: {total_chunks}")


if __name__ == "__main__":
    ingest()
