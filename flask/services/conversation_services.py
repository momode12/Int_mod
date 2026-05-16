from datetime import datetime, timezone, timedelta

from bson import ObjectId

from models.conversation_models import conversation_schema, message_schema
from services.chat_services import ChatService

EAT = timezone(timedelta(hours=3))

def _oid(raw: str) -> ObjectId:
    try:
        return ObjectId(raw)
    except Exception:
        raise ValueError(f"ID invalide: {raw}")


def _fmt_conv(doc: dict) -> dict:
    return {
        "id":               str(doc["_id"]),
        "nom_conversation": doc.get("nom_conversation", ""),
        "created_at":       doc["created_at"].isoformat(),
        "updated_at":       doc.get("updated_at", doc["created_at"]).isoformat(),
    }


def _fmt_msg(doc: dict) -> dict:
    return {
        "id":          str(doc["_id"]),
        "texte":       doc.get("texte"),
        "categorie":   doc.get("categorie"),
        "label_fr":    doc.get("label_fr"),
        "icon":        doc.get("icon"),
        "confidence":  doc.get("confidence"),
        "indicator":   doc.get("indicator"),
        "tfidf_sim":   doc.get("tfidf_sim"),
        "medicament1": doc.get("medicament1"),
        "medicament2": doc.get("medicament2"),
        "astuce":      doc.get("astuce"),
        "generated":   doc.get("generated"),
        "top3":        doc.get("top3", []),
        "alerte":      doc.get("alerte"),
        "fallback":    doc.get("fallback"),
        "ood":         doc.get("ood"),
        "created_at":  doc["created_at"].isoformat(),
    }


def _get_conv(db, conv_id: str, user_id: str) -> dict:

    oid = _oid(conv_id)   # ValueError si invalide
    doc = db.conversations.find_one({"_id": oid, "user_id": user_id})
    if not doc:
        raise LookupError("Conversation introuvable")
    return doc

class ConversationService:

    @staticmethod
    def list(db, user_id: str) -> list:

        docs = list(
            db.conversations.find(
                {"user_id": user_id},
                sort=[("updated_at", -1)],
            )
        )
        return [_fmt_conv(d) for d in docs]

    @staticmethod
    def create(db, user_id: str, nom: str = "Nouvelle conversation") -> dict:

        nom = (nom or "Nouvelle conversation").strip()
        doc = conversation_schema(user_id, nom)
        res = db.conversations.insert_one(doc)
        doc["_id"] = res.inserted_id
        return _fmt_conv(doc)

    @staticmethod
    def get(db, conv_id: str, user_id: str) -> dict:

        conv     = _get_conv(db, conv_id, user_id)
        messages = list(
            db.messages.find(
                {"conversation_id": conv_id},
                sort=[("created_at", 1)],
            )
        )
        payload             = _fmt_conv(conv)
        payload["messages"] = [_fmt_msg(m) for m in messages]
        return payload

    @staticmethod
    def rename(db, conv_id: str, user_id: str, nom: str) -> dict:

        if not nom or not nom.strip():
            raise ValueError("nom_conversation requis")

        conv = _get_conv(db, conv_id, user_id)
        now  = datetime.now(EAT)

        db.conversations.update_one(
            {"_id": conv["_id"]},
            {"$set": {"nom_conversation": nom.strip(), "updated_at": now}},
        )
        conv["nom_conversation"] = nom.strip()
        conv["updated_at"]       = now
        return _fmt_conv(conv)

    @staticmethod
    def delete(db, conv_id: str, user_id: str) -> dict:

        conv = _get_conv(db, conv_id, user_id)
        db.messages.delete_many({"conversation_id": conv_id})
        db.conversations.delete_one({"_id": conv["_id"]})
        return {"message": "Conversation supprimée"}

    @staticmethod
    def send(db, conv_id: str, user_id: str, texte: str) -> dict:
        # 1. Vérification ownership
        conv = _get_conv(db, conv_id, user_id)

        # 2. Contexte session — dernière catégorie médicale connue
        last_msg = db.messages.find_one(
            {"conversation_id": conv_id, "ood": {"$ne": True}},
            sort=[("created_at", -1)],
        )
        session_last_cat = last_msg.get("categorie") if last_msg else None

        # 3. Pipeline NLP
        svc    = ChatService.get()
        result = svc.chat(texte, session_last_cat=session_last_cat)

        # 4a. Salutation → pas de persistance
        if result.get("type") == "salutation":
            return {"type": "salutation", "response": result["response"]}

        # 4b. Persistance du message + résultat NLP
        msg_doc = message_schema(
            conversation_id = conv_id,
            texte           = texte,
            categorie       = result.get("categorie"),
            label_fr        = result.get("label_fr"),
            icon            = result.get("icon"),
            confidence      = result.get("confidence"),
            indicator       = result.get("indicator"),
            tfidf_sim       = result.get("tfidf_sim"),
            medicament1     = result.get("medicament1"),
            medicament2     = result.get("medicament2"),
            astuce          = result.get("astuce"),
            generated       = result.get("generated"),
            top3            = result.get("top3"),
            alerte          = result.get("alerte"),
            fallback        = result.get("fallback"),
            ood             = result.get("ood", False),
        )
        ins        = db.messages.insert_one(msg_doc)
        message_id = str(ins.inserted_id)
        created_at = msg_doc["created_at"]

        # 5. Touch updated_at conversation
        db.conversations.update_one(
            {"_id": conv["_id"]},
            {"$set": {"updated_at": created_at}},
        )

        # 6. Réponse formatée
        return {
            "message_id":  message_id,
            "type":        result.get("type"),
            "created_at":  created_at.isoformat(),
            "categorie":   result.get("categorie"),
            "label_fr":    result.get("label_fr"),
            "icon":        result.get("icon"),
            "confidence":  result.get("confidence"),
            "indicator":   result.get("indicator"),
            "tfidf_sim":   result.get("tfidf_sim"),
            "medicament1": result.get("medicament1"),
            "medicament2": result.get("medicament2"),
            "astuce":      result.get("astuce"),
            "generated":   result.get("generated"),
            "top3":        result.get("top3", []),
            "alerte":      result.get("alerte"),
            "fallback":    result.get("fallback"),
            "ood":         result.get("ood", False),
        }