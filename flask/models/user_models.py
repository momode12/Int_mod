from datetime import datetime, timedelta, timezone

EAT = timezone(timedelta(hours=3))


def create_user_collection(db):
    if "users" not in db.list_collection_names():
        db.create_collection("users")
        print("Collection 'users' créée")

    db.users.create_index("email", unique=True)
    print("Index email créé")

def user_schema(name: str, email: str, hashed_password: str) -> dict:
    return {
        "name":       name,
        "email":      email,
        "password":   hashed_password,
        "avatar":     None,
        "role":       "user",
        "created_at": datetime.now(EAT),
        "updated_at": datetime.now(EAT),
    }