import uuid
from qdrant_client.models import PointStruct, VectorParams, Distance
from db.qdrant_client import client
from session.intent_router import route_intent

# -----------------------------
# CONFIG
# -----------------------------
SESSION_COLLECTION = "session_memory"
VECTOR_SIZE = 768


# -----------------------------
# INIT COLLECTION
# -----------------------------
def init_session_collection():
    try:
        client.get_collection(SESSION_COLLECTION)
    except Exception:
        client.create_collection(
            collection_name=SESSION_COLLECTION,
            vectors_config=VectorParams(
                size=VECTOR_SIZE,
                distance=Distance.COSINE
            )
        )


# -----------------------------
# CREATE SESSION
# -----------------------------
def create_session():
    session_id = str(uuid.uuid4())

    client.upsert(
        collection_name=SESSION_COLLECTION,
        points=[
            PointStruct(
                id=session_id,
                vector=[0.0] * VECTOR_SIZE,  # dummy vector
                payload={
                    "profile_text": "",
                    "exclusion_texts": [],
                    "shown_schemes": [],
                    "intent_log": [],
                    "pending_clarification": None
                }
            )
        ]
    )

    return session_id


# -----------------------------
# GET SESSION
# -----------------------------
def get_session(session_id: str):
    result = client.retrieve(
        collection_name=SESSION_COLLECTION,
        ids=[session_id]
    )

    if not result:
        return {}

    return result[0].payload


# -----------------------------
# UPDATE PROFILE / EXCLUSIONS
# -----------------------------
def update_profile_from_text(session_id: str, text: str):
    session = get_session(session_id)

    profile = session.get("profile_text", "")
    exclusions = session.get("exclusion_texts", [])
    shown = session.get("shown_schemes", [])
    intent_log = session.get("intent_log", [])
    pending = session.get("pending_clarification")

    routing = route_intent(text)

    # -----------------------------
    # MERGE CLARIFICATION ANSWER
    # -----------------------------
    if pending and routing["intent"] == "positive":
        text = f"{pending} {text}"
        pending = None  # clear after merge

    # -----------------------------
    # HANDLE INTENT
    # -----------------------------
    if routing["intent"] == "positive":
        profile = (profile + " " + text).strip()
        note = "Eligibility context added."

    elif routing["intent"] == "negative":
        exclusions.append(text)
        note = "Exclusion noted."

    elif routing["intent"] == "clarify":
        # store ambiguous statement and ask question
        pending = text

        client.upsert(
            collection_name=SESSION_COLLECTION,
            points=[
                PointStruct(
                    id=session_id,
                    vector=[0.0] * VECTOR_SIZE,
                    payload={
                        "profile_text": profile,
                        "exclusion_texts": exclusions,
                        "shown_schemes": shown,
                        "intent_log": intent_log,
                        "pending_clarification": pending
                    }
                )
            ]
        )

        return routing["message"]

    else:  # ignore
        note = "Input noted (no profile update)."

    # -----------------------------
    # LOG INTENT
    # -----------------------------
    intent_log.append({
        "text": text,
        "intent": routing["intent"],
        "positive_score": routing.get("positive_score", 0.0),
        "negative_score": routing.get("negative_score", 0.0)
    })

    # -----------------------------
    # SAVE SESSION
    # -----------------------------
    client.upsert(
        collection_name=SESSION_COLLECTION,
        points=[
            PointStruct(
                id=session_id,
                vector=[0.0] * VECTOR_SIZE,
                payload={
                    "profile_text": profile,
                    "exclusion_texts": list(set(exclusions)),
                    "shown_schemes": shown,
                    "intent_log": intent_log,
                    "pending_clarification": pending
                }
            )
        ]
    )

    return note


# -----------------------------
# UPDATE SHOWN SCHEMES
# -----------------------------
def update_session(session_id: str, scheme_names):
    session = get_session(session_id)

    client.upsert(
        collection_name=SESSION_COLLECTION,
        points=[
            PointStruct(
                id=session_id,
                vector=[0.0] * VECTOR_SIZE,
                payload={
                    "profile_text": session.get("profile_text", ""),
                    "exclusion_texts": session.get("exclusion_texts", []),
                    "shown_schemes": scheme_names,
                    "intent_log": session.get("intent_log", []),
                    "pending_clarification": session.get("pending_clarification")
                }
            )
        ]
    )


# -----------------------------
# CLEAR SESSION MEMORY
# -----------------------------
def clear_session_memory(session_id: str):
    client.upsert(
        collection_name=SESSION_COLLECTION,
        points=[
            PointStruct(
                id=session_id,
                vector=[0.0] * VECTOR_SIZE,
                payload={
                    "profile_text": "",
                    "exclusion_texts": [],
                    "shown_schemes": [],
                    "intent_log": [],
                    "pending_clarification": None
                }
            )
        ]
    )

    return "Session memory cleared."
