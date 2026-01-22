import uuid
import shutil
import pytesseract
from PIL import Image

from sentence_transformers import SentenceTransformer
from qdrant_client.models import PointStruct, VectorParams, Distance
from db.qdrant_client import client

# -----------------------------
# OCR SETUP (SYSTEM ONLY)
# -----------------------------
TESSERACT_PATH = shutil.which("tesseract")

if TESSERACT_PATH:
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH
else:
    pytesseract.pytesseract.tesseract_cmd = None

TESSERACT_AVAILABLE = pytesseract.pytesseract.tesseract_cmd is not None

# -----------------------------
# CONFIG
# -----------------------------
EMBED_MODEL = "sentence-transformers/all-mpnet-base-v2"
VECTOR_SIZE = 768
CHUNK_SIZE = 800

_model = None  # lazy-loaded model

# -----------------------------
# HELPERS
# -----------------------------
def get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer(EMBED_MODEL)
    return _model


def chunk_text(text, size=CHUNK_SIZE):
    return [text[i:i + size] for i in range(0, len(text), size)]


def ensure_collection(collection_name):
    try:
        client.get_collection(collection_name)
    except Exception:
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(
                size=VECTOR_SIZE,
                distance=Distance.COSINE
            )
        )

# -----------------------------
# INGEST IMAGE
# -----------------------------
def ingest_image_for_session(session_id: str, image_path: str) -> bool:

    if not TESSERACT_AVAILABLE:
        print(
            "OCR is unavailable.\n"
            "Please install Tesseract OCR system-wide and ensure it is in PATH."
        )
        return False

    collection_name = f"user_docs_{session_id}"
    ensure_collection(collection_name)

    try:
        with Image.open(image_path) as image:
            text = pytesseract.image_to_string(image).strip()
    except Exception as e:
        print(f"OCR failed: {e}")
        return False

    if not text:
        print("No text found in image.")
        return False

    chunks = chunk_text(text)
    model = get_model()
    vectors = model.encode(chunks)

    points = []
    for chunk, vector in zip(chunks, vectors):
        points.append(
            PointStruct(
                id=str(uuid.uuid4()),
                vector=vector.tolist(),
                payload={
                    "source": "user_upload",
                    "file_type": "image",
                    "file_name": image_path,
                    "text": chunk
                }
            )
        )

    client.upsert(collection_name=collection_name, points=points)
    print("Image ingested successfully.")
    return True
