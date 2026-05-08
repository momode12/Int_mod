from flask import Flask
from flask_cors import CORS
from pymongo import MongoClient
from config import Config
from models.user_models import create_user_collection
from models.conversation_models import create_conversation_collections
from models.chatbot_model import load_chatbot
from routes import api_bp
from flasgger import Swagger

def create_app():

    app = Flask(__name__)

    Swagger(app, template={
        "swagger": "2.0",
        "info": {
            "title": "ChatBot API",
            "version": "1.0"
        },
        "securityDefinitions": {
            "Bearer": {
                "type"       : "apiKey",
                "name"       : "Authorization",
                "in"         : "header",
                "description": "Format: Bearer <token>"
            }
        }
    })

    CORS(app,
         resources={r"/*": {
             "origins"            : ["http://localhost:3000", "http://localhost:5173"],
             "methods"            : ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
             "allow_headers"      : ["Content-Type", "Authorization"],
             "expose_headers"     : ["Content-Type", "Authorization"],
             "supports_credentials": True
         }})

    # Connexion MongoDB
    client = MongoClient(Config.MONGO_URI)
    db = client.get_default_database()
    app.db = db

    # Collections crees automatiquement
    create_user_collection(db)
    create_conversation_collections(db)

    # Chargement du modele IA 
    try:
        load_chatbot(app)
    except FileNotFoundError:
        print("model_files/ incomplet — placez les 4 fichiers Colab dans model_files/")
        app.chatbot = None
    except Exception as e:
        print(f"Erreur modele IA : {e}")
        app.chatbot = None

    # Blueprint principal
    app.register_blueprint(api_bp)

    @app.route("/")
    def index():
        return {"message": "ChatBot IA API — operationnelle"}

    return app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
