def is_ambiguous_income(text: str) -> bool:
    text = text.lower()

    has_number = any(ch.isdigit() for ch in text)
    mentions_income = any(
        kw in text for kw in ["income", "earn", "salary"]
    )

    has_unit = any(
        unit in text for unit in ["per month", "monthly", "per year", "annual"]
    )

    return has_number and mentions_income and not has_unit

def contains_negation(text: str) -> bool:
    text = text.lower()
    return any(
        neg in text
        for neg in [" not ", " not.", " not,", " no ", " don't ", " do not ", " exclude "]
    )
IGNORED_UTTERANCES = {
    "ok",
    "hi",
    "hello",
    "hey",
    "okay",
    "yes",
    "yeah",
    "yep",
    "hmm",
    "hmmm",
    "sure",
    "next",
    "continue",
    "go on",
    "show more",
    "tell me more",
    "thanks",
    "thank you"
}


# intent_router.py

from sentence_transformers import SentenceTransformer
import numpy as np

# -----------------------------
# MODEL (LOAD ONCE)
# -----------------------------
model = SentenceTransformer("sentence-transformers/all-mpnet-base-v2")

def embed(texts):
    return model.encode(texts, normalize_embeddings=True)


def cosine(a, b):
    return float(np.dot(a, b))


# -----------------------------
# INTENT ANCHORS
# -----------------------------
POSITIVE_ANCHORS = [
    "I am eligible for",
    "I want schemes for",
    "I am a",
    "I belong to",
    "schemes applicable to me",
    "I am looking for benefits related to",
    "my income is",
    "i earn",
    "my monthly income is",
    "income less than",
    "income below",
    "annual income is",
    "my salary is"
]

NEGATIVE_ANCHORS = [
    "I am not eligible for",
    "I am not",
    "exclude schemes related to",
    "these schemes do not apply to me",
    "I do not want schemes for",
    "not applicable in my case",
    "I should not be shown schemes related to"
]

POS_ANCHOR_VECS = embed(POSITIVE_ANCHORS)
NEG_ANCHOR_VECS = embed(NEGATIVE_ANCHORS)


# -----------------------------
# ROUTING FUNCTION
# -----------------------------
def route_intent(user_text: str) -> dict:
    text = user_text.strip().lower()

    # -----------------------------
    # HARD IGNORE (cheap, deterministic)
    # -----------------------------
    if text in IGNORED_UTTERANCES:
        return {
            "intent": "ignore",
            "positive_score": 0.0,
            "negative_score": 0.0
        }

    # -----------------------------
    # AMBIGUOUS INCOME → CLARIFY
    # -----------------------------
    if is_ambiguous_income(user_text):
        return {
            "intent": "clarify",
            "message": "Is this monthly or annual income?",
            "positive_score": 0.0,
            "negative_score": 0.0
        }

    # -----------------------------
    # SEMANTIC ROUTING
    # -----------------------------
    u_vec = embed([user_text])[0]

    # Always compute base similarities
    pos_sim = max(cosine(u_vec, v) for v in POS_ANCHOR_VECS)
    neg_sim = max(cosine(u_vec, v) for v in NEG_ANCHOR_VECS)

    # Negation bias (tie-breaker)
    negation_bias = 0.08 if contains_negation(user_text) else 0.0
    adjusted_neg_sim = neg_sim + negation_bias

    # Confidence gating
    max_sim = max(pos_sim, adjusted_neg_sim)

    if max_sim < 0.25:
        intent = "ignore"
    else:
        MARGIN = 0.05
        if adjusted_neg_sim > pos_sim + MARGIN:
            intent = "negative"
        else:
            intent = "positive"

    return {
        "intent": intent,
        "positive_score": round(pos_sim, 3),
        "negative_score": round(adjusted_neg_sim, 3)
    }
