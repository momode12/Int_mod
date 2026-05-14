from datetime import datetime, timezone, timedelta

EAT = timezone(timedelta(hours=3)) 

def create_conversation_collections(db):

    existing = db.list_collection_names()

    if "conversations" not in existing:
        db.create_collection("conversations")
        print("Collection 'conversations' crée")

    if "messages" not in existing:
        db.create_collection("messages")
        print("Collection 'messages' crée")

    db.conversations.create_index("user_id")
    db.conversations.create_index([("user_id", 1), ("updated_at", -1)])
    db.messages.create_index("conversation_id")
    db.messages.create_index([("conversation_id", 1), ("created_at", 1)])
    print("Index conversations et messages crée")
    
def conversation_schema(user_id: str, nom_conversation: str = "Nouvelle conversation") -> dict:
    now = datetime.now(EAT)
    return {
        "user_id":          user_id,
        "nom_conversation": nom_conversation,
        "created_at":       now,
        "updated_at":       now,
    }


def message_schema(
    conversation_id: str,
    texte: str,
    categorie: str | None        = None,
    label_fr: str | None         = None,
    icon: str | None             = None,
    confidence: float | None     = None,
    indicator: str | None        = None,   
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
        "created_at":      datetime.now(EAT),
    }