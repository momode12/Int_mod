from flask import Blueprint, request, jsonify, current_app
from middlewares.auth_middleware import token_required

user_bp = Blueprint("user", __name__, url_prefix="/user")

@user_bp.route("/profile", methods=["GET"])
@token_required
def profile():
    user = request.user

    return jsonify({
        "id": str(user["_id"]),
        "name": user["name"],
        "email": user["email"]
    })