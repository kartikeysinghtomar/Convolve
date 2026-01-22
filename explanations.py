# explanations.py

from sentence_transformers.util import cos_sim

# -----------------------------
# WHY SHOWN
# -----------------------------
def build_why_shown(session, top_k=2):
    """
    Builds a human-readable explanation for why a scheme was shown,
    based on recent positive intents.
    """
    intent_log = session.get("intent_log", [])

    positive_reasons = [
        e["text"]
        for e in reversed(intent_log)
        if e["intent"] == "positive"
    ][:top_k]

    if not positive_reasons:
        return "Shown because it matches your overall profile."

    return (
        "Shown because it matches your profile: "
        + "; ".join(positive_reasons)
    )


# -----------------------------
# WHY EXCLUDED
# -----------------------------
def find_exclusion_reason(
    scheme_embedding,
    exclusion_texts,
    exclusion_embeddings,
    threshold=0.55
):
    """
    Returns the exclusion text that caused this scheme to be removed,
    or None if no exclusion applies.
    """
    for text, emb in zip(exclusion_texts, exclusion_embeddings):
        sim = cos_sim(scheme_embedding, emb).item()
        if sim >= threshold:
            return text

    return None
