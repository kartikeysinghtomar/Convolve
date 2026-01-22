from sentence_transformers import SentenceTransformer
from qdrant_client.models import Filter, FieldCondition, MatchAny
from session.memory import get_session, update_session
from retrieval.search_user_docs import get_user_doc_context
from explanations import build_why_shown
import numpy as np

# -----------------------------
# CONFIG
# -----------------------------
COLLECTION_NAME = "schemes_index"
EMBED_MODEL = "sentence-transformers/all-mpnet-base-v2"
TOP_K = 20
THRESHOLD = 0.3
EXCLUSION_THRESHOLD = 0.55

model = SentenceTransformer(EMBED_MODEL)

from db.qdrant_client import client

LAST_RESULTS = []
LAST_REASONS = {}   # scheme_name -> list of reasons

# -----------------------------
# STATE LIST
# -----------------------------
INDIAN_STATES = [
    "andhra pradesh", "arunachal pradesh", "assam", "bihar", "chhattisgarh",
    "goa", "gujarat", "haryana", "himachal pradesh", "jharkhand", "karnataka",
    "kerala", "madhya pradesh", "maharashtra", "manipur", "meghalaya",
    "mizoram", "nagaland", "odisha", "punjab", "rajasthan", "sikkim",
    "tamil nadu", "telangana", "tripura", "uttar pradesh", "uttarakhand",
    "west bengal", "jammu and kashmir", "ladakh", "delhi", "chandigarh",
    "puducherry", "dadra and nagar haveli", "daman and diu",
    "andaman and nicobar"
]

def detect_state(text: str):
    text = text.lower()
    for state in INDIAN_STATES:
        if state in text:
            return state.title()
    return None

# -----------------------------
# COSINE SIM
# -----------------------------
def cosine_similarity(a, b):
    a = np.array(a)
    b = np.array(b)
    return float(a @ b) / (np.linalg.norm(a) * np.linalg.norm(b))

# -----------------------------
# SEMANTIC EXCLUSION
# -----------------------------
def exclusion_reason(
    scheme_vec,
    exclusion_texts,
    exclusion_embeddings
):
    """
    Returns the exclusion text that caused this scheme to be removed,
    or None if not excluded.
    """
    if not exclusion_embeddings:
        return None

    for text, emb in zip(exclusion_texts, exclusion_embeddings):
        score = cosine_similarity(scheme_vec, emb)
        if score >= EXCLUSION_THRESHOLD:
            return text

    return None

# -----------------------------
# MAIN SEARCH
# -----------------------------
def discover_schemes_for_session(session_id: str):
    global LAST_RESULTS, LAST_REASONS
    LAST_RESULTS = []
    LAST_REASONS = {}

    session = get_session(session_id)
    profile_text = session.get("profile_text", "").strip()
    exclusion_texts = session.get("exclusion_texts", [])

    doc_context = get_user_doc_context(
        session_id,
        "government schemes eligibility benefits application"
    )

    if not profile_text and not doc_context:
        print("\nNo profile or uploaded document information available.\n")
        return

    # -----------------------------
    # QUERY BUILD
    # -----------------------------
    query_text = f"{profile_text} {doc_context}".strip()
    query_vector = model.encode(query_text).tolist()

    detected_state = detect_state(query_text)

    query_filter = None
    if detected_state:
        query_filter = Filter(
            should=[
                FieldCondition(
                    key="valid_states",
                    match=MatchAny(any=[detected_state])
                ),
                FieldCondition(
                    key="valid_states",
                    match=MatchAny(any=["All India"])
                )
            ]
        )

    # -----------------------------
    # SEARCH
    # -----------------------------
    # 1. Build query text
    query_text = f"{profile_text} {doc_context}".strip()

    if not query_text:
        print("\nNo profile or document context available.\n")
        return

    # 2. Embed query text
    query_vector = model.encode(query_text).tolist()


    results = client.search(
    collection_name=COLLECTION_NAME,
    query_vector=query_vector,
    query_filter=query_filter,
    limit=TOP_K
)

    if not results:
        print("\nNo schemes found.\n")
        return


    candidates = [r for r in results if r.score >= THRESHOLD]

    if not candidates:
        print("\nNo relevant schemes found. Try adding more details.\n")
        return

    exclusion_embeddings = (
        model.encode(exclusion_texts)
        if exclusion_texts else []
    )

    final = []

    for r in candidates:
        payload = r.payload
        name = payload.get("scheme_name", "Unknown Scheme")

        LAST_REASONS[name] = []

        LAST_REASONS[name].append(
            f"Semantic relevance score: {r.score:.2f}"
        )

        if detected_state:
            LAST_REASONS[name].append(
                f"Eligible for {detected_state} or All India"
            )
        else:
            LAST_REASONS[name].append(
                "No state specified; ranked semantically"
            )

        # -----------------------------
        # BUILD SCHEME VECTOR
        # -----------------------------
        scheme_text = " ".join([
            payload.get("scheme_name", ""),
            payload.get("eligibility", ""),
            payload.get("schemeCategory", ""),
            " ".join(payload.get("tags", []))
        ]).strip()

        scheme_vec = model.encode(scheme_text)

        # -----------------------------
        # SEMANTIC EXCLUSION
        # -----------------------------
        reason = exclusion_reason(
            scheme_vec,
            exclusion_texts,
            exclusion_embeddings
        )

        if reason:
            LAST_REASONS[name].append(
                f"Excluded because you said: '{reason}'"
            )
            continue

        # -----------------------------
        # WHY SHOWN
        # -----------------------------
        why_shown = build_why_shown(session)
        LAST_REASONS[name].append(why_shown)

        final.append(r)

    if not final:
        print("\nAll matching schemes were excluded based on your preferences.\n")
        return

    # -----------------------------
    # OUTPUT
    # -----------------------------
    print("\nSchemes you may benefit from:\n")

    for i, r in enumerate(final, start=1):
        payload = r.payload
        name = payload.get("scheme_name", "Unknown Scheme")

        print(f"{i}. {name}")
        if payload.get("schemeCategory"):
            print(f"   Category: {payload['schemeCategory']}")
        if payload.get("valid_states"):
            print(f"   States: {payload['valid_states']}")
        print()

        LAST_RESULTS.append(payload)

    update_session(
        session_id,
        [p.get("scheme_name") for p in LAST_RESULTS]
    )

# -----------------------------
# SCHEME MENU
# -----------------------------
def scheme_action_menu(index: int):
    scheme = LAST_RESULTS[index]
    name = scheme.get("scheme_name", "Unknown Scheme")

    while True:
        print("\nChoose an option:")
        print("1. Who is eligible?")
        print("2. What benefits are provided?")
        print("3. How to apply?")
        print("4. What documents are required?")
        print("5. Why was this scheme shown?")
        print("6. Back to scheme list")

        choice = input(">> ").strip()

        if choice == "1":
            print("\nEligibility:\n", scheme.get("eligibility", "Not available"))
        elif choice == "2":
            print("\nBenefits:\n", scheme.get("benefits", "Not available"))
        elif choice == "3":
            print("\nHow to apply:\n", scheme.get("application", "Not available"))
        elif choice == "4":
            print("\nDocuments required:\n", scheme.get("documents", "Not available"))
        elif choice == "5":
            print("\nReason Trace:")
            for r in LAST_REASONS.get(name, []):
                print(f"• {r}")
        elif choice == "6":
            return "BACK_TO_LIST"
        else:
            print("Invalid option.")

# -----------------------------
# ACCESS LAST RESULTS
# -----------------------------
def get_last_results():
    return LAST_RESULTS
