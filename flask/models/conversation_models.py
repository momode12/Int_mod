from datetime import datetime


# ---------------------------------------------------------------------------
# Collection setup
# ---------------------------------------------------------------------------

def create_conversation_collections(db):
    """
    Create MongoDB collections and indexes for conversations and messages.
    Safe to call every startup (create_collection is idempotent via the guard).
    """
    existing = db.list_collection_names()

    if "conversations" not in existing:
        db.create_collection("conversations")
        print("✅ Collection 'conversations' créée")

    if "messages" not in existing:
        db.create_collection("messages")
        print("✅ Collection 'messages' créée")

    # Indexes
    db.conversations.create_index("user_id")
    db.conversations.create_index([("user_id", 1), ("updated_at", -1)])
    db.messages.create_index("conversation_id")
    db.messages.create_index([("conversation_id", 1), ("created_at", 1)])
    print("✅ Index conversations/messages créés")


# ---------------------------------------------------------------------------
# Document schemas  (plain dicts — no ODM)
# ---------------------------------------------------------------------------

def conversation_schema(user_id: str, nom_conversation: str = "Nouvelle conversation") -> dict:
    now = datetime.utcnow()
    return {
        "user_id":          user_id,
        "nom_conversation": nom_conversation,
        "created_at":       now,
        "updated_at":       now,
    }


def message_schema(
    conversation_id: str,
    texte: str,
    # --- NLP fields produced by chat_services.chat() ---
    categorie: str | None        = None,
    label_fr: str | None         = None,
    icon: str | None             = None,
    confidence: float | None     = None,
    indicator: str | None        = None,   # "green" | "yellow" | "red"
    tfidf_sim: float | None      = None,
    medicament1: str | None      = None,
    medicament2: str | None      = None,
    astuce: str | None           = None,
    generated: str | None        = None,
    top3: list | None            = None,
    alerte: str | None           = None,
    fallback: str | None         = None,
    ood: bool | None             = None,
) -> dict:
    return {
        "conversation_id": conversation_id,
        "texte":           texte,
        # NLP output
        "categorie":       categorie,
        "label_fr":        label_fr,
        "icon":            icon,
        "confidence":      confidence,
        "indicator":       indicator,
        "tfidf_sim":       tfidf_sim,
        "medicament1":     medicament1,
        "medicament2":     medicament2,
        "astuce":          astuce,
        "generated":       generated,
        "top3":            top3 or [],
        "alerte":          alerte,
        "fallback":        fallback,
        "ood":             ood,
        "created_at":      datetime.utcnow(),
    }