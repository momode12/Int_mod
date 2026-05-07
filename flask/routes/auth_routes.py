from flask import Blueprint, request, jsonify, current_app
from services.auth_services import register_user, login_user

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

@auth_bp.route("/register", methods=["POST"])
def register():
    """
    Créer un nouveau compte utilisateur
    ---
    tags:
      - Authentification
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - name
            - email
            - password
          properties:
            name:
              type: string
              example: Jean Rakoto
            email:
              type: string
              example: jean@example.com
            password:
              type: string
              example: motdepasse123
    responses:
      201:
        description: Compte créé avec succès
        schema:
          type: object
          properties:
            token:
              type: string
              example: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
            user:
              type: object
              properties:
                id:
                  type: string
                name:
                  type: string
                email:
                  type: string
      400:
        description: Champs manquants ou mot de passe trop court
        schema:
          type: object
          properties:
            message:
              type: string
              example: Tous les champs sont requis
      409:
        description: Email déjà utilisé
        schema:
          type: object
          properties:
            message:
              type: string
              example: Email déjà utilisé
      500:
        description: Erreur serveur
    """
    try:
        data = request.get_json()

        name     = data.get("name", "").strip()
        email    = data.get("email", "").strip().lower()
        password = data.get("password", "")

        if not name or not email or not password:
            return jsonify({"message": "Tous les champs sont requis"}), 400

        if len(password) < 6:
            return jsonify({"message": "Mot de passe trop court (min 6 caractères)"}), 400

        db     = current_app.db
        result = register_user(db, name, email, password)

        return jsonify(result), 201

    except ValueError as e:
        return jsonify({"message": str(e)}), 409
    except Exception as e:
        return jsonify({"message": str(e)}), 500

@auth_bp.route("/login", methods=["POST"])
def login():
    """
    Se connecter avec email et mot de passe
    ---
    tags:
      - Authentification
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - email
            - password
          properties:
            email:
              type: string
              example: jean@example.com
            password:
              type: string
              example: motdepasse123
    responses:
      200:
        description: Connexion réussie
        schema:
          type: object
          properties:
            token:
              type: string
              example: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
            user:
              type: object
              properties:
                id:
                  type: string
                name:
                  type: string
                email:
                  type: string
      400:
        description: Email et mot de passe requis
        schema:
          type: object
          properties:
            message:
              type: string
              example: Email et mot de passe requis
      401:
        description: Email ou mot de passe incorrect
        schema:
          type: object
          properties:
            message:
              type: string
              example: Email ou mot de passe incorrect
      500:
        description: Erreur serveur
    """
    try:
        data = request.get_json()

        email    = data.get("email", "").strip().lower()
        password = data.get("password", "")

        if not email or not password:
            return jsonify({"message": "Email et mot de passe requis"}), 400

        db     = current_app.db
        result = login_user(db, email, password)

        return jsonify(result), 200

    except ValueError as e:
        return jsonify({"message": str(e)}), 401
    except Exception as e:
        return jsonify({"message": str(e)}), 500