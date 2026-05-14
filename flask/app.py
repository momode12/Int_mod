from flask import Flask
from flask_cors import CORS
from pymongo import MongoClient
from config import Config
from models.user_models import create_user_collection
from models.conversation_models import create_conversation_collections
from routes import api_bp
from flasgger import Swagger

def create_app():
    app = Flask(__name__)

    Swagger(app, template={
        "swagger": "2.0",
        "info": {
            "title": "ChatBot Médical Malagasy API",
            "version": "1.0"
        },
        "securityDefinitions": {
            "Bearer": {
                "type":        "apiKey",
                "name":        "Authorization",
                "in":          "header",
                "description": "Format: Bearer <token>"
            }
        }
    })

    CORS(app,
         resources={r"/*": {
             "origins":             ["http://localhost:3000", "http://localhost:5173"],
             "methods":             ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
             "allow_headers":       ["Content-Type", "Authorization"],
             "expose_headers":      ["Content-Type", "Authorization"],
             "supports_credentials": True,
         }})

    client   = MongoClient(Config.MONGO_URI)
    db       = client.get_default_database()
    app.db   = db

    create_user_collection(db)
    create_conversation_collections(db)

    from services.chat_services import ChatService
    ChatService.get()

    app.register_blueprint(api_bp)

    @app.route("/")
    def index():
        return {"message": "ChatBot Médical Malagasy API — opérationnelle"}

    return app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)