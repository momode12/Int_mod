from functools import wraps
from flask import request, jsonify, current_app
from services.auth_services import decode_token
from bson import ObjectId

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            auth_header = request.headers.get("Authorization")

            # ❌ pas de header
            if not auth_header:
                return jsonify({"message": "Token manquant"}), 401

            # ❌ format invalide
            parts = auth_header.split()
            if len(parts) != 2 or parts[0] != "Bearer":
                return jsonify({"message": "Format du token invalide"}), 401

            token = parts[1]

            # ✅ decode JWT
            payload = decode_token(token)
            user_id = payload.get("user_id")

            # ❌ user introuvable
            db = current_app.db
            user = db.users.find_one({"_id": ObjectId(user_id)})

            if not user:
                return jsonify({"message": "Utilisateur introuvable"}), 401

            # inject user dans request
            request.user = user

            return f(*args, **kwargs)

        except Exception as e:
            print("JWT ERROR:", str(e))
            return jsonify({"message": "Token invalide ou expiré"}), 401

    return decorated