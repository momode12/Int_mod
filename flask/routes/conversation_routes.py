from flask import Blueprint, request, jsonify, current_app
from middlewares.auth_middleware   import token_required
from services.conversation_service import (
    create_conversation,
    get_conversations,
    get_conversation_by_id,
    rename_conversation,
    delete_conversation,
    send_message,
    get_messages,
)
from services.chatbot_service import get_all_categories

conversation_bp = Blueprint("conversation", __name__, url_prefix="/conversations")

@conversation_bp.route("", methods=["POST"])
@token_required
def create():
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
        required: true
        schema:
          type: object
          required:
            - nom_conversation
          properties:
            nom_conversation:
              type: string
              example: Consultation du 22 avril
    responses:
      201:
        description: Conversation créée avec succès
        schema:
          type: object
          properties:
            id:
              type: string
              example: 664a1b2c3d4e5f6789abcdef
            nom_conversation:
              type: string
              example: Consultation du 22 avril
            created_at:
              type: string
              example: 2025-04-22T10:30:00
      400:
        description: nom_conversation requis
        schema:
          type: object
          properties:
            message:
              type: string
              example: nom_conversation requis
      401:
        description: Token invalide ou expiré
      500:
        description: Erreur serveur
    """
    try:
        data             = request.get_json()
        nom_conversation = data.get("nom_conversation", "").strip()

        if not nom_conversation:
            return jsonify({"message": "nom_conversation requis"}), 400

        db      = current_app.db
        user_id = str(request.user["_id"])
        result  = create_conversation(db, user_id, nom_conversation)

        return jsonify(result), 201

    except Exception as e:
        return jsonify({"message": str(e)}), 500

@conversation_bp.route("", methods=["GET"])
@token_required
def get_all():
    """
    Récupérer toutes mes conversations
    ---
    tags:
      - Conversations
    security:
      - Bearer: []
    responses:
      200:
        description: Liste des conversations de l'utilisateur connecté
        schema:
          type: array
          items:
            type: object
            properties:
              id:
                type: string
                example: 664a1b2c3d4e5f6789abcdef
              nom_conversation:
                type: string
                example: Consultation du 22 avril
              created_at:
                type: string
                example: 2025-04-22T10:30:00
              updated_at:
                type: string
                example: 2025-04-22T11:00:00
      401:
        description: Token invalide ou expiré
      500:
        description: Erreur serveur
    """
    try:
        db      = current_app.db
        user_id = str(request.user["_id"])
        result  = get_conversations(db, user_id)

        return jsonify(result), 200

    except Exception as e:
        return jsonify({"message": str(e)}), 500


# ══════════════════════════════════════════
# GET /api/conversations/:id
# ══════════════════════════════════════════
@conversation_bp.route("/<conversation_id>", methods=["GET"])
@token_required
def get_one(conversation_id):
    """
    Récupérer une conversation avec tous ses messages
    ---
    tags:
      - Conversations
    security:
      - Bearer: []
    parameters:
      - in: path
        name: conversation_id
        type: string
        required: true
        description: ID de la conversation
        example: 664a1b2c3d4e5f6789abcdef
    responses:
      200:
        description: Conversation avec historique des messages
        schema:
          type: object
          properties:
            id:
              type: string
            nom_conversation:
              type: string
            created_at:
              type: string
            updated_at:
              type: string
            messages:
              type: array
              items:
                type: object
                properties:
                  id:
                    type: string
                  texte:
                    type: string
                  categorie:
                    type: string
                  confidence:
                    type: number
                  medicament1:
                    type: string
                  medicament2:
                    type: string
                  astuce:
                    type: string
                  created_at:
                    type: string
      401:
        description: Token invalide ou expiré
      404:
        description: Conversation introuvable
        schema:
          type: object
          properties:
            message:
              type: string
              example: Conversation introuvable
      500:
        description: Erreur serveur
    """
    try:
        db      = current_app.db
        user_id = str(request.user["_id"])
        result  = get_conversation_by_id(db, conversation_id, user_id)

        return jsonify(result), 200

    except ValueError as e:
        return jsonify({"message": str(e)}), 404
    except Exception as e:
        return jsonify({"message": str(e)}), 500

@conversation_bp.route("/<conversation_id>", methods=["PUT"])
@token_required
def rename(conversation_id):
    """
    Renommer une conversation
    ---
    tags:
      - Conversations
    security:
      - Bearer: []
    parameters:
      - in: path
        name: conversation_id
        type: string
        required: true
        description: ID de la conversation
        example: 664a1b2c3d4e5f6789abcdef
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
              example: Consultation suivi semaine 2
    responses:
      200:
        description: Conversation renommée
        schema:
          type: object
          properties:
            message:
              type: string
              example: Conversation renommee
            nom_conversation:
              type: string
              example: Consultation suivi semaine 2
      400:
        description: nom_conversation requis
      401:
        description: Token invalide ou expiré
      404:
        description: Conversation introuvable
      500:
        description: Erreur serveur
    """
    try:
        data = request.get_json()
        nom  = data.get("nom_conversation", "").strip()

        if not nom:
            return jsonify({"message": "nom_conversation requis"}), 400

        db      = current_app.db
        user_id = str(request.user["_id"])
        result  = rename_conversation(db, conversation_id, user_id, nom)

        return jsonify(result), 200

    except ValueError as e:
        return jsonify({"message": str(e)}), 404
    except Exception as e:
        return jsonify({"message": str(e)}), 500


# ══════════════════════════════════════════
# DELETE /api/conversations/:id
# ══════════════════════════════════════════
@conversation_bp.route("/<conversation_id>", methods=["DELETE"])
@token_required
def delete(conversation_id):
    """
    Supprimer une conversation et tous ses messages
    ---
    tags:
      - Conversations
    security:
      - Bearer: []
    parameters:
      - in: path
        name: conversation_id
        type: string
        required: true
        description: ID de la conversation à supprimer
        example: 664a1b2c3d4e5f6789abcdef
    responses:
      200:
        description: Conversation supprimée
        schema:
          type: object
          properties:
            message:
              type: string
              example: Conversation supprimee
      401:
        description: Token invalide ou expiré
      404:
        description: Conversation introuvable
      500:
        description: Erreur serveur
    """
    try:
        db      = current_app.db
        user_id = str(request.user["_id"])
        result  = delete_conversation(db, conversation_id, user_id)

        return jsonify(result), 200

    except ValueError as e:
        return jsonify({"message": str(e)}), 404
    except Exception as e:
        return jsonify({"message": str(e)}), 500

@conversation_bp.route("/<conversation_id>/chat", methods=["POST"])
@token_required
def chat(conversation_id):
    """
    Envoyer un message — l'IA répond et tout est sauvegardé en base
    ---
    tags:
      - Chatbot IA
    security:
      - Bearer: []
    parameters:
      - in: path
        name: conversation_id
        type: string
        required: true
        description: ID de la conversation
        example: 664a1b2c3d4e5f6789abcdef
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
              example: Marary ny lohako indrindra rehefa maraina vao mifoha
    responses:
      200:
        description: Réponse de l'IA sauvegardée en base MongoDB
        schema:
          type: object
          properties:
            message_id:
              type: string
              example: 664a1b2c3d4e5f6789abcdef
            texte:
              type: string
              example: Marary ny lohako indrindra rehefa maraina vao mifoha
            categorie:
              type: string
              example: aretin-doha
            icon:
              type: string
              example: "\U0001f9e0"
            confidence:
              type: number
              example: 90.2
            indicator:
              type: string
              enum:
                - green
                - yellow
                - red
              example: green
            medicament1:
              type: string
              example: "Paracétamol 500 mg : 3x/andro"
            medicament2:
              type: string
              example: "Ibuprofène 400 mg : 2x/andro"
            astuce:
              type: string
              example: "Misotroa rano betsaka ary matory ampy 7-8 ora"
            generated:
              type: string
              example: "paracetamol 500 mg maraina midi hariva"
            top3:
              type: array
              items:
                type: object
                properties:
                  categorie:
                    type: string
                  icon:
                    type: string
                  score:
                    type: number
            alerte:
              type: string
              nullable: true
              description: Message d'alerte si symptôme grave détecté
              example: null
            fallback:
              type: string
              nullable: true
              description: Conseil générique si confiance < 40%
              example: null
            created_at:
              type: string
              example: 2025-04-22T10:30:00
      400:
        description: Texte manquant, trop court ou trop long
        schema:
          type: object
          properties:
            message:
              type: string
              example: Champ texte requis
      401:
        description: Token invalide ou expiré
      404:
        description: Conversation introuvable
      500:
        description: Erreur serveur
    """
    try:
        if current_app.chatbot is None:
            return jsonify({"message": "Modele IA non charge"}), 503

        data  = request.get_json()
        texte = data.get("texte", "").strip()

        if not texte:
            return jsonify({"message": "Champ texte requis"}), 400

        if len(texte) < 3:
            return jsonify({"message": "Texte trop court (min 3 caractères)"}), 400

        if len(texte) > 500:
            return jsonify({"message": "Texte trop long (max 500 caractères)"}), 400

        db      = current_app.db
        user_id = str(request.user["_id"])
        result  = send_message(db, conversation_id, user_id, texte)

        return jsonify(result), 200

    except ValueError as e:
        return jsonify({"message": str(e)}), 404
    except Exception as e:
        return jsonify({"message": str(e)}), 500


# ══════════════════════════════════════════
# GET /api/conversations/:id/messages
# ══════════════════════════════════════════
@conversation_bp.route("/<conversation_id>/messages", methods=["GET"])
@token_required
def messages(conversation_id):
    """
    Récupérer l'historique des messages d'une conversation
    ---
    tags:
      - Chatbot IA
    security:
      - Bearer: []
    parameters:
      - in: path
        name: conversation_id
        type: string
        required: true
        description: ID de la conversation
        example: 664a1b2c3d4e5f6789abcdef
    responses:
      200:
        description: Historique complet des messages
        schema:
          type: array
          items:
            type: object
            properties:
              id:
                type: string
              texte:
                type: string
              categorie:
                type: string
              confidence:
                type: number
              indicator:
                type: string
                enum:
                  - green
                  - yellow
                  - red
              medicament1:
                type: string
              medicament2:
                type: string
              astuce:
                type: string
              generated:
                type: string
              top3:
                type: array
                items:
                  type: object
              alerte:
                type: string
                nullable: true
              fallback:
                type: string
                nullable: true
              created_at:
                type: string
      401:
        description: Token invalide ou expiré
      404:
        description: Conversation introuvable
      500:
        description: Erreur serveur
    """
    try:
        db      = current_app.db
        user_id = str(request.user["_id"])
        result  = get_messages(db, conversation_id, user_id)

        return jsonify(result), 200

    except ValueError as e:
        return jsonify({"message": str(e)}), 404
    except Exception as e:
        return jsonify({"message": str(e)}), 500

@conversation_bp.route("/categories", methods=["GET"])
@token_required
def categories():
    """
    Récupérer la liste des 28 catégories médicales disponibles
    ---
    tags:
      - Chatbot IA
    security:
      - Bearer: []
    responses:
      200:
        description: Liste des catégories médicales
        schema:
          type: object
          properties:
            total:
              type: integer
              example: 28
            categories:
              type: array
              items:
                type: object
                properties:
                  id:
                    type: string
                    example: aretin-doha
                  label_fr:
                    type: string
                    example: Maux de tete
                  icon:
                    type: string
                    example: "\U0001f9e0"
      401:
        description: Token invalide ou expiré
      503:
        description: Modèle IA non chargé
    """
    try:
        if current_app.chatbot is None:
            return jsonify({"message": "Modele IA non charge"}), 503

        cats = get_all_categories()
        return jsonify({"total": len(cats), "categories": cats}), 200

    except Exception as e:
        return jsonify({"message": str(e)}), 500

@conversation_bp.route("/health", methods=["GET"])
def health():
    """
    Vérifier l'état du modèle IA
    ---
    tags:
      - Chatbot IA
    responses:
      200:
        description: Modèle IA opérationnel
        schema:
          type: object
          properties:
            status:
              type: string
              example: ok
            model:
              type: object
              properties:
                classes:
                  type: integer
                  example: 28
                device:
                  type: string
                  example: cpu
      503:
        description: Modèle IA non chargé
        schema:
          type: object
          properties:
            status:
              type: string
              example: error
            message:
              type: string
              example: Modele non charge
    """
    try:
        if current_app.chatbot is None:
            return jsonify({"status": "error", "message": "Modele non charge"}), 503

        chatbot = current_app.chatbot
        return jsonify({
            "status": "ok",
            "model" : {
                "classes": len(chatbot["idx2category"]),
                "device" : "cpu",
            }
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 503
