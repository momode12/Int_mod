from datetime import datetime


def create_conversation_collections(db):
    if "conversations" not in db.list_collection_names():
        db.create_collection("conversations")
        print("Collection 'conversations' creee")

    if "messages" not in db.list_collection_names():
        db.create_collection("messages")
        print("Collection 'messages' creee")

    db.conversations.create_index("user_id")
    db.messages.create_index("conversation_id")
    db.messages.create_index("user_id")
    print("Index conversations et messages crees")


def conversation_schema(user_id, nom_conversation: str) -> dict:
    return {
        "user_id"         : user_id,
        "nom_conversation": nom_conversation,
        "created_at"      : datetime.utcnow(),
        "updated_at"      : datetime.utcnow(),
    }


def message_schema(conversation_id, user_id, texte: str, result: dict) -> dict:
    return {
        "conversation_id": conversation_id,
        "user_id"        : user_id,
        "texte"          : texte,
        "categorie"      : result.get("categorie"),
        "confidence"     : result.get("confidence"),
        "indicator"      : result.get("indicator"),
        "medicament1"    : result.get("medicament1"),
        "medicament2"    : result.get("medicament2"),
        "astuce"         : result.get("astuce"),
        "generated"      : result.get("generated"),
        "top3"           : result.get("top3"),
        "alerte"         : result.get("alerte"),
        "created_at"     : datetime.utcnow(),
    }
