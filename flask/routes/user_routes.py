from flask import Blueprint, request, jsonify, current_app
from middlewares.auth_middleware import token_required
from bson import ObjectId
from datetime import datetime

user_bp = Blueprint("user", __name__, url_prefix="/user")

@user_bp.route("/profile", methods=["GET"])
@token_required
def profile():
    """
    Récupérer le profil de l'utilisateur connecté
    ---
    tags:
      - Utilisateur
    security:
      - Bearer: []
    responses:
      200:
        description: Profil utilisateur
        schema:
          type: object
          properties:
            id:
              type: string
              example: 664a1b2c3d4e5f6789abcdef
            name:
              type: string
              example: Jean Rakoto
            email:
              type: string
              example: jean@example.com
            role:
              type: string
              example: user
            created_at:
              type: string
              example: 2025-04-21T10:30:00
      401:
        description: Token invalide ou expiré
        schema:
          type: object
          properties:
            message:
              type: string
              example: Token invalide ou expiré
    """
    user = request.user
    return jsonify({
        "id"        : str(user["_id"]),
        "name"      : user["name"],
        "email"     : user["email"],
        "role"      : user.get("role", "user"),
        "created_at": user["created_at"].isoformat() if "created_at" in user else None,
    }), 200

@user_bp.route("/profile", methods=["PUT"])
@token_required
def update_profile():
    """
    Modifier le nom de l'utilisateur connecté
    ---
    tags:
      - Utilisateur
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            name:
              type: string
              example: Jean Rakoto Nouveau
    responses:
      200:
        description: Profil mis à jour
        schema:
          type: object
          properties:
            message:
              type: string
              example: Profil mis à jour
            name:
              type: string
      400:
        description: Nom requis
      401:
        description: Token invalide ou expiré
      500:
        description: Erreur serveur
    """
    try:
        data = request.get_json()
        name = data.get("name", "").strip()

        if not name:
            return jsonify({"message": "Nom requis"}), 400

        db = current_app.db
        db.users.update_one(
            {"_id": request.user["_id"]},
            {"$set": {"name": name, "updated_at": datetime.utcnow()}}
        )
        return jsonify({"message": "Profil mis à jour", "name": name}), 200

    except Exception as e:
        return jsonify({"message": str(e)}), 500