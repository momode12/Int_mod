import bcrypt
import jwt
from datetime import datetime, timedelta, timezone
from config import Config

EAT = timezone(timedelta(hours=3)) 

def hash_password(password: str) -> str:
    return bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")
    
def verify_password(password: str, hashed: str) -> bool:
    if not isinstance(password, str):
        raise ValueError("Mot de passe invalide")

    return bcrypt.checkpw(
        password.encode("utf-8"),
        hashed.encode("utf-8")
    )

def generate_token(user_id: str) -> str:
    payload = {
        "user_id": user_id,
        "exp":     datetime.now(EAT) + timedelta(seconds=Config.JWT_EXPIRATION)
    }
    return jwt.encode(payload, Config.JWT_SECRET, algorithm="HS256")

def decode_token(token: str) -> dict:
    return jwt.decode(
        token,
        Config.JWT_SECRET,
        algorithms=["HS256"]
    )

def register_user(db, name: str, email: str, password: str) -> dict:
    from models.user_models import user_schema

    existing = db.users.find_one({"email": email})
    if existing:
        raise ValueError("Email déjà utilisé")

    hashed = hash_password(password)
    user   = user_schema(name, email, hashed)

    result  = db.users.insert_one(user)
    user_id = str(result.inserted_id)
    token   = generate_token(user_id)

    return {
        "token": token,
        "user": {
            "id":    user_id,
            "name":  name,
            "email": email,
        }
    }

def login_user(db, email: str, password: str) -> dict:
    user = db.users.find_one({"email": email})

    if not user:
        raise ValueError("Email ou mot de passe incorrect")

    if not verify_password(password, user["password"]):
        raise ValueError("Email ou mot de passe incorrect")

    user_id = str(user["_id"])
    token   = generate_token(user_id)

    return {
        "token": token,
        "user": {
            "id":    user_id,
            "name":  user["name"],
            "email": user["email"],
        }
    }