import uuid
import fitz
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, VectorParams, Distance
import shutil

TESSERACT_AVAILABLE = shutil.which("tesseract") is not None

EMBED_MODEL = "sentence-transformers/all-mpnet-base-v2"
VECTOR_SIZE = 768
CHUNK_SIZE = 800

model = SentenceTransformer(EMBED_MODEL)
from db.qdrant_client import client


def chunk_text(text, size=CHUNK_SIZE):
    return [text[i:i + size] for i in range(0, len(text), size)]


def ensure_collection(collection):
    try:
        client.get_collection(collection)
    except Exception:
        try:
            client.create_collection(
                collection_name=collection,
                vectors_config=VectorParams(
                    size=VECTOR_SIZE,
                    distance=Distance.COSINE
                )
            )
        except Exception as e:
            if "already exists" not in str(e).lower():
                raise e


def ingest_pdf_for_session(session_id: str, pdf_path: str):
    if not TESSERACT_AVAILABLE:
        print(
            "OCR is unavailable because Tesseract is not installed.\n"
        "Please install Tesseract OCR to enable image processing."
        )
    return

    collection = f"user_docs_{session_id}"
    ensure_collection(collection)

    doc = fitz.open(pdf_path)

    for page_num, page in enumerate(doc, start=1):
        text = page.get_text().strip()
        if not text:
            continue

        chunks = chunk_text(text)
        vectors = model.encode(chunks)

        points = []
        for chunk, vector in zip(chunks, vectors):
            points.append(
                PointStruct(
                    id=str(uuid.uuid4()),
                    vector=vector.tolist(),
                    payload={
                        "source": "user_upload",
                        "file_type": "pdf",
                        "file_name": pdf_path,
                        "page": page_num,
                        "text": chunk
                    }
                )
            )

        client.upsert(collection_name=collection, points=points)
