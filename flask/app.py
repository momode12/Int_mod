from flask import Flask, g
from flask_cors import CORS
from pymongo import MongoClient
from config import Config
from models.user_models import create_user_collection
from routes import api_bp

def create_app():
    app = Flask(__name__)
    CORS(app, 
         resources={r"/*": {
             "origins": ["http://localhost:3000", "http://localhost:5173"],
             "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
             "allow_headers": ["Content-Type", "Authorization"],
             "expose_headers": ["Content-Type", "Authorization"],
             "supports_credentials": True
         }})

    # ✅ Connexion MongoDB
    client = MongoClient(Config.MONGO_URI)
    db     = client.get_default_database()

    # ✅ Stocker db dans app directement
    app.db = db

    # ✅ Collections créées automatiquement
    create_user_collection(db)

    # ✅ Blueprint principal
    app.register_blueprint(api_bp)

    @app.route("/")
    def index():
        return {"message": "ChatBot IA API — opérationnelle ✅"}

    return app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)