"""
conversation_routes.py
~~~~~~~~~~~~~~~~~~~~~~
REST endpoints consumed by the React ChatProvider:

  GET    /api/conversations                         → list
  POST   /api/conversations                         → create
  GET    /api/conversations/<id>                    → detail + messages
  PUT    /api/conversations/<id>                    → rename
  DELETE /api/conversations/<id>                    → delete
  POST   /api/conversations/<id>/chat               → send message → NLP response
"""

from datetime import datetime

from bson import ObjectId
from flask import Blueprint, current_app, jsonify, request

from middlewares.auth_middleware import token_required
from models.conversation_models import conversation_schema, message_schema
from services.chat_services import ChatService

conversation_bp = Blueprint("conversation", __name__, url_prefix="/conversations")


# ── helpers ──────────────────────────────────────────────────────────────────

def _oid(raw: str):
    """Convert string → ObjectId; raise ValueError on invalid input."""
    try:
        return ObjectId(raw)
    except Exception:
        raise ValueError(f"ID invalide: {raw}")


def _fmt_conv(doc: dict) -> dict:
    """Serialize a conversations document for the API response."""
    return {
        "id":               str(doc["_id"]),
        "nom_conversation": doc.get("nom_conversation", ""),
        "created_at":       doc["created_at"].isoformat(),
        "updated_at":       doc.get("updated_at", doc["created_at"]).isoformat(),
    }


def _fmt_msg(doc: dict) -> dict:
    """Serialize a messages document for the API response."""
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


def _get_conv_or_404(db, conv_id: str, user_id: str):
    """Return the conversation doc or raise a 404-style tuple."""
    try:
        oid = _oid(conv_id)
    except ValueError:
        return None, (jsonify({"message": "ID invalide"}), 400)

    doc = db.conversations.find_one({"_id": oid, "user_id": user_id})
    if not doc:
        return None, (jsonify({"message": "Conversation introuvable"}), 404)
    return doc, None


# ── routes ───────────────────────────────────────────────────────────────────

@conversation_bp.route("", methods=["GET"])
@token_required
def list_conversations():
    """
    GET /api/conversations
    Return all conversations for the authenticated user, newest first.
    """
    db      = current_app.db
    user_id = str(request.user["_id"])

    docs = list(
        db.conversations.find(
            {"user_id": user_id},
            sort=[("updated_at", -1)],
        )
    )
    return jsonify([_fmt_conv(d) for d in docs]), 200


@conversation_bp.route("", methods=["POST"])
@token_required
def create_conversation():
    """
    POST /api/conversations
    Body: { "nom_conversation": "..." }  (optional)
    """
    db      = current_app.db
    user_id = str(request.user["_id"])
    data    = request.get_json(silent=True) or {}

    nom  = (data.get("nom_conversation") or "Nouvelle conversation").strip()
    doc  = conversation_schema(user_id, nom)
    res  = db.conversations.insert_one(doc)
    doc["_id"] = res.inserted_id

    return jsonify(_fmt_conv(doc)), 201


@conversation_bp.route("/<conv_id>", methods=["GET"])
@token_required
def get_conversation(conv_id: str):
    """
    GET /api/conversations/<conv_id>
    Returns conversation metadata + its messages array.
    """
    db      = current_app.db
    user_id = str(request.user["_id"])

    conv, err = _get_conv_or_404(db, conv_id, user_id)
    if err:
        return err

    messages = list(
        db.messages.find(
            {"conversation_id": conv_id},
            sort=[("created_at", 1)],
        )
    )

    payload = _fmt_conv(conv)
    payload["messages"] = [_fmt_msg(m) for m in messages]
    return jsonify(payload), 200


@conversation_bp.route("/<conv_id>", methods=["PUT"])
@token_required
def update_conversation(conv_id: str):
    """
    PUT /api/conversations/<conv_id>
    Body: { "nom_conversation": "..." }
    """
    db      = current_app.db
    user_id = str(request.user["_id"])

    conv, err = _get_conv_or_404(db, conv_id, user_id)
    if err:
        return err

    data = request.get_json(silent=True) or {}
    nom  = (data.get("nom_conversation") or "").strip()
    if not nom:
        return jsonify({"message": "nom_conversation requis"}), 400

    now = datetime.utcnow()
    db.conversations.update_one(
        {"_id": conv["_id"]},
        {"$set": {"nom_conversation": nom, "updated_at": now}},
    )
    conv["nom_conversation"] = nom
    conv["updated_at"]       = now
    return jsonify(_fmt_conv(conv)), 200


@conversation_bp.route("/<conv_id>", methods=["DELETE"])
@token_required
def delete_conversation(conv_id: str):
    """
    DELETE /api/conversations/<conv_id>
    Also removes all messages belonging to the conversation.
    """
    db      = current_app.db
    user_id = str(request.user["_id"])

    conv, err = _get_conv_or_404(db, conv_id, user_id)
    if err:
        return err

    db.messages.delete_many({"conversation_id": conv_id})
    db.conversations.delete_one({"_id": conv["_id"]})
    return jsonify({"message": "Conversation supprimée"}), 200


@conversation_bp.route("/<conv_id>/chat", methods=["POST"])
@token_required
def send_message(conv_id: str):
    """
    POST /api/conversations/<conv_id>/chat
    Body: { "texte": "marary ny lohako" }

    Runs the NLP pipeline and persists the message + result.
    Response shape matches ApiChatResponse expected by the React frontend:
      { message_id, type, created_at, ...all NLP fields... }
    or for salutations:
      { type: "salutation", response: "..." }
    """
    db      = current_app.db
    user_id = str(request.user["_id"])

    conv, err = _get_conv_or_404(db, conv_id, user_id)
    if err:
        return err

    data  = request.get_json(silent=True) or {}
    texte = (data.get("texte") or "").strip()
    if not texte:
        return jsonify({"message": "texte requis"}), 400

    # Retrieve last category for session context (last message in this conv)
    last_msg = db.messages.find_one(
        {"conversation_id": conv_id, "ood": {"$ne": True}},
        sort=[("created_at", -1)],
    )
    session_last_cat = last_msg.get("categorie") if last_msg else None

    # ── Run NLP ──────────────────────────────────────────────────────
    svc    = ChatService.get()
    result = svc.chat(texte, session_last_cat=session_last_cat)

    # Salutation — no persistence needed, return immediately
    if result.get("type") == "salutation":
        return jsonify({"type": "salutation", "response": result["response"]}), 200

    # ── Persist message ───────────────────────────────────────────────
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

    # Touch conversation updated_at
    db.conversations.update_one(
        {"_id": conv["_id"]},
        {"$set": {"updated_at": created_at}},
    )

    # ── Response ─────────────────────────────────────────────────────
    return jsonify({
        "message_id":  message_id,
        "type":        result.get("type"),
        "created_at":  created_at.isoformat(),
        # NLP fields
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
    }), 200