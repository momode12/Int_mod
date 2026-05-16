from flask import Blueprint, request, jsonify, current_app
from middlewares.auth_middleware import token_required
from bson import ObjectId
from datetime import datetime, timedelta, timezone

EAT = timezone(timedelta(hours=3))

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
      401:
        description: Token invalide ou expiré
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
      400:
        description: Nom requis
      401:
        description: Token invalide ou expiré
      500:
        description: Erreur serveur
    """
    try:
        data = request.get_json()
        name  = data.get("name", "").strip()
        email = data.get("email", "").strip().lower()

        if not name and not email:
            return jsonify({"message": "Nom ou email requis"}), 400

        db = current_app.db
        updates = {"updated_at": datetime.now(EAT)}
        if name:
            updates["name"] = name

        if email and email != request.user.get("email"):
            existing = db.users.find_one({
                "email": email,
                "_id"  : {"$ne": request.user["_id"]},
            })
            if existing:
                return jsonify({"message": "Email déjà utilisé"}), 409
            updates["email"] = email

        db.users.update_one(
            {"_id": request.user["_id"]},
            {"$set": updates}
        )

        updated = db.users.find_one({"_id": request.user["_id"]})
        return jsonify({
            "message": "Profil mis à jour",
            "user": {
                "id"   : str(updated["_id"]),
                "name" : updated.get("name"),
                "email": updated.get("email"),
            }
        }), 200

    except Exception as e:
        return jsonify({"message": str(e)}), 500
