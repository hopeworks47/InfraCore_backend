from app.core.security import hash_password, verify_password


async def get_user_by_email(db, email: str):
    return await db.users.find_one({"email": email})

async def fetch_users(db):
    return await db.users.find().to_list(length=None)

async def create_user(db, email: str, password: str):
    user = {
        "email": email,
        "hashed_password": hash_password(password)
    }
    result = await db.users.insert_one(user)
    user["_id"] = str(result.inserted_id)
    return user


async def authenticate_user(db, email: str, password: str):
    user = await get_user_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user["hashed_password"]):
        return None
    return user