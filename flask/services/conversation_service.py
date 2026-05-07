from datetime import datetime
from bson import ObjectId

from models.conversation_models import conversation_schema, message_schema
from services.chatbot_service   import (
    predict_symptome,
    detect_salutation,
    CATEGORY_ICONS,
    CATEGORY_LABELS_FR,
)


def create_conversation(db, user_id: str, nom_conversation: str) -> dict:
    conv   = conversation_schema(ObjectId(user_id), nom_conversation)
    result = db.conversations.insert_one(conv)

    return {
        "id"              : str(result.inserted_id),
        "nom_conversation": nom_conversation,
        "created_at"      : conv["created_at"].isoformat(),
    }


def get_conversations(db, user_id: str) -> list:
    convs = db.conversations.find(
        {"user_id": ObjectId(user_id)},
        sort=[("updated_at", -1)]
    )
    return [
        {
            "id"              : str(c["_id"]),
            "nom_conversation": c["nom_conversation"],
            "created_at"      : c["created_at"].isoformat(),
            "updated_at"      : c["updated_at"].isoformat(),
        }
        for c in convs
    ]


def get_conversation_by_id(db, conversation_id: str, user_id: str) -> dict:
    conv = db.conversations.find_one({
        "_id"    : ObjectId(conversation_id),
        "user_id": ObjectId(user_id),
    })
    if not conv:
        raise ValueError("Conversation introuvable")

    messages = list(db.messages.find(
        {"conversation_id": ObjectId(conversation_id)},
        sort=[("created_at", 1)]
    ))
    return {
        "id"              : str(conv["_id"]),
        "nom_conversation": conv["nom_conversation"],
        "created_at"      : conv["created_at"].isoformat(),
        "updated_at"      : conv["updated_at"].isoformat(),
        "messages"        : [_format_message(m) for m in messages],
    }


def rename_conversation(db, conversation_id: str, user_id: str, nom: str) -> dict:
    result = db.conversations.update_one(
        {"_id": ObjectId(conversation_id), "user_id": ObjectId(user_id)},
        {"$set": {"nom_conversation": nom, "updated_at": datetime.utcnow()}}
    )
    if result.matched_count == 0:
        raise ValueError("Conversation introuvable")
    return {"message": "Conversation renommee", "nom_conversation": nom}


def delete_conversation(db, conversation_id: str, user_id: str) -> dict:
    result = db.conversations.delete_one({
        "_id"    : ObjectId(conversation_id),
        "user_id": ObjectId(user_id),
    })
    if result.deleted_count == 0:
        raise ValueError("Conversation introuvable")

    db.messages.delete_many({"conversation_id": ObjectId(conversation_id)})
    return {"message": "Conversation supprimee"}


def send_message(db, conversation_id: str, user_id: str, texte: str) -> dict:
    # Verifier que la conversation appartient a l'utilisateur
    conv = db.conversations.find_one({
        "_id"    : ObjectId(conversation_id),
        "user_id": ObjectId(user_id),
    })
    if not conv:
        raise ValueError("Conversation introuvable")

    # Verifier si c'est une salutation
    salutation = detect_salutation(texte)
    if salutation:
        result = {
            "categorie"  : "salutation",
            "confidence" : 100.0,
            "indicator"  : "green",
            "medicament1": None,
            "medicament2": None,
            "astuce"     : None,
            "generated"  : salutation,
            "top3"       : [],
            "alerte"     : None,
            "fallback"   : None,
        }

        msg      = message_schema(ObjectId(conversation_id), ObjectId(user_id), texte, result)
        inserted = db.messages.insert_one(msg)

        db.conversations.update_one(
            {"_id": ObjectId(conversation_id)},
            {"$set": {"updated_at": datetime.utcnow()}}
        )

        return {
            "message_id" : str(inserted.inserted_id),
            "type"       : "salutation",
            "texte"      : texte,
            "categorie"  : result["categorie"],
            "icon"       : "👋",
            "confidence" : result["confidence"],
            "indicator"  : result["indicator"],
            "medicament1": result["medicament1"],
            "medicament2": result["medicament2"],
            "astuce"     : result["astuce"],
            "generated"  : result["generated"],
            "top3"       : result["top3"],
            "alerte"     : result["alerte"],
            "fallback"   : result["fallback"],
            "created_at" : msg["created_at"].isoformat(),
        }

    # Appel IA
    result = predict_symptome(texte)

    # Sauvegarder en base
    msg      = message_schema(ObjectId(conversation_id), ObjectId(user_id), texte, result)
    inserted = db.messages.insert_one(msg)

    # Mettre a jour updated_at de la conversation
    db.conversations.update_one(
        {"_id": ObjectId(conversation_id)},
        {"$set": {"updated_at": datetime.utcnow()}}
    )

    return {
        "message_id" : str(inserted.inserted_id),
        "texte"      : texte,
        "categorie"  : result["categorie"],
        "icon"       : result["icon"],
        "confidence" : result["confidence"],
        "indicator"  : result["indicator"],
        "medicament1": result["medicament1"],
        "medicament2": result["medicament2"],
        "astuce"     : result["astuce"],
        "generated"  : result["generated"],
        "top3"       : result["top3"],
        "alerte"     : result["alerte"],
        "fallback"   : result["fallback"],
        "created_at" : msg["created_at"].isoformat(),
    }


def get_messages(db, conversation_id: str, user_id: str) -> list:
    conv = db.conversations.find_one({
        "_id"    : ObjectId(conversation_id),
        "user_id": ObjectId(user_id),
    })
    if not conv:
        raise ValueError("Conversation introuvable")

    messages = list(db.messages.find(
        {"conversation_id": ObjectId(conversation_id)},
        sort=[("created_at", 1)]
    ))
    return [_format_message(m) for m in messages]


def _format_message(m: dict) -> dict:
    categorie = m.get("categorie")
    icon      = CATEGORY_ICONS.get(categorie, "") if categorie else ""
    label_fr  = CATEGORY_LABELS_FR.get(categorie, categorie) if categorie else None
    return {
        "id"         : str(m["_id"]),
        "texte"      : m.get("texte"),
        "categorie"  : m.get("categorie"),
        "label_fr"   : label_fr,
        "icon"       : icon,
        "confidence" : m.get("confidence"),
        "indicator"  : m.get("indicator"),
        "medicament1": m.get("medicament1"),
        "medicament2": m.get("medicament2"),
        "astuce"     : m.get("astuce"),
        "generated"  : m.get("generated"),
        "top3"       : m.get("top3"),
        "alerte"     : m.get("alerte"),
        "fallback"   : m.get("fallback"),
        "created_at" : m["created_at"].isoformat(),
    }
