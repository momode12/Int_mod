from flask import Blueprint, current_app, jsonify, request

from middlewares.auth_middleware import token_required
from services.conversation_services import ConversationService

conversation_bp = Blueprint("conversation", __name__, url_prefix="/conversations")

def _handle(fn):

    try:
        return fn()
    except ValueError as e:
        return jsonify({"message": str(e)}), 400
    except LookupError as e:
        return jsonify({"message": str(e)}), 404

@conversation_bp.route("", methods=["GET"])
@token_required
def list_conversations():
    """
    Lister toutes les conversations de l'utilisateur connecté
    ---
    tags:
      - Conversations
    security:
      - Bearer: []
    responses:
      200:
        description: Liste des conversations triées par date de mise à jour décroissante
      401:
        description: Token invalide ou expiré
    """
    user_id = str(request.user["_id"])
    result  = ConversationService.list(current_app.db, user_id)
    return jsonify(result), 200


@conversation_bp.route("", methods=["POST"])
@token_required
def create_conversation():
    """
    Créer une nouvelle conversation
    ---
    tags:
      - Conversations
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        schema:
          type: object
          properties:
            nom_conversation:
              type: string
              example: Nouvelle conversation
    responses:
      201:
        description: Conversation crée
      401:
        description: Token invalide ou expiré
    """
    user_id = str(request.user["_id"])
    data    = request.get_json(silent=True) or {}
    nom     = data.get("nom_conversation", "Nouvelle conversation")

    result  = ConversationService.create(current_app.db, user_id, nom)
    return jsonify(result), 201


@conversation_bp.route("/<conv_id>", methods=["GET"])
@token_required
def get_conversation(conv_id: str):
    """
    Récupérer une conversation avec tous ses messages
    ---
    tags:
      - Conversations
    security:
      - Bearer: []
    parameters:
      - in: path
        name: conv_id
        type: string
        required: true
        description: ID MongoDB de la conversation
        example: 6a05a0b111ee3a898d2c6eab
    responses:
      200:
        description: Conversation avec ses messages
      401:
        description: Token invalide ou expiré
      404:
        description: Conversation introuvable
    """
    user_id = str(request.user["_id"])
    return _handle(
        lambda: (jsonify(ConversationService.get(current_app.db, conv_id, user_id)), 200)
    )


@conversation_bp.route("/<conv_id>", methods=["PUT"])
@token_required
def update_conversation(conv_id: str):
    """
    Renommer une conversation
    ---
    tags:
      - Conversations
    security:
      - Bearer: []
    parameters:
      - in: path
        name: conv_id
        type: string
        required: true
        description: ID MongoDB de la conversation
        example: 6a05a0b111ee3a898d2c6eab
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - nom_conversation
          properties:
            nom_conversation:
              type: string
              example: Marary ny lohako
    responses:
      200:
        description: Conversation renommée
      400:
        description: nom_conversation requis
      401:
        description: Token invalide ou expiré
      404:
        description: Conversation introuvable
    """
    user_id = str(request.user["_id"])
    data    = request.get_json(silent=True) or {}
    nom     = data.get("nom_conversation", "")

    return _handle(
        lambda: (
            jsonify(ConversationService.rename(current_app.db, conv_id, user_id, nom)),
            200,
        )
    )


@conversation_bp.route("/<conv_id>", methods=["DELETE"])
@token_required
def delete_conversation(conv_id: str):
    """
    Supprimer une conversation et tous ses messages
    ---
    tags:
      - Conversations
    security:
      - Bearer: []
    parameters:
      - in: path
        name: conv_id
        type: string
        required: true
        description: ID MongoDB de la conversation
        example: 6a05a0b111ee3a898d2c6eab
    responses:
      200:
        description: Conversation supprimée avec succès
      401:
        description: Token invalide ou expiré
      404:
        description: Conversation introuvable
    """
    user_id = str(request.user["_id"])
    return _handle(
        lambda: (
            jsonify(ConversationService.delete(current_app.db, conv_id, user_id)),
            200,
        )
    )


@conversation_bp.route("/<conv_id>/chat", methods=["POST"])
@token_required
def send_message(conv_id: str):
    """
    Envoyer un message et obtenir une réponse du chatbot médical malagasy
    ---
    tags:
      - Conversations
    security:
      - Bearer: []
    parameters:
      - in: path
        name: conv_id
        type: string
        required: true
        description: ID MongoDB de la conversation
        example: 6a05a0b111ee3a898d2c6eab
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - texte
          properties:
            texte:
              type: string
              example: marary ny lohako
    responses:
      200:
        description: Réponse du chatbot NLP. 
      400:
        description: texte requis ou ID invalide
      401:
        description: Token invalide ou expiré
      404:
        description: Conversation introuvable
    """
    user_id = str(request.user["_id"])
    data    = request.get_json(silent=True) or {}
    texte   = (data.get("texte") or "").strip()

    if not texte:
        return jsonify({"message": "texte requis"}), 400

    return _handle(
        lambda: (
            jsonify(ConversationService.send(current_app.db, conv_id, user_id, texte)),
            200,
        )
    )