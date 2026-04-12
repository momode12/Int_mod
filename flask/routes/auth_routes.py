from flask import Blueprint, request, jsonify, current_app
from services.auth_services import register_user, login_user

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

@auth_bp.route("/register", methods=["POST"])
def register():
    try:
        data = request.get_json()
        print("📥 Register data reçue:", data)

        name     = data.get("name", "").strip()
        email    = data.get("email", "").strip().lower()
        password = data.get("password", "")

        if not name or not email or not password:
            return jsonify({"message": "Tous les champs sont requis"}), 400

        if len(password) < 6:
            return jsonify({"message": "Mot de passe trop court"}), 400

        db     = current_app.db
        result = register_user(db, name, email, password)
        print("✅ User créé:", result["user"])
        return jsonify(result), 201

    except ValueError as e:
        print("⚠️ ValueError:", str(e))
        return jsonify({"message": str(e)}), 409
    except Exception as e:
        print("❌ Erreur:", str(e))
        return jsonify({"message": str(e)}), 500


@auth_bp.route("/login", methods=["POST"])
def login():
    try:
        data = request.get_json()
        print("📥 Login data reçue:", data)

        email    = data.get("email", "").strip().lower()
        password = data.get("password", "")

        if not email or not password:
            return jsonify({"message": "Email et mot de passe requis"}), 400

        db     = current_app.db
        result = login_user(db, email, password)
        print("✅ User connecté:", result["user"])
        return jsonify(result), 200

    except ValueError as e:
        print("⚠️ ValueError:", str(e))
        return jsonify({"message": str(e)}), 401
    except Exception as e:
        print("❌ Erreur:", str(e))
        return jsonify({"message": str(e)}), 500