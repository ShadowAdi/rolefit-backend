import os
from dotenv import load_dotenv
from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone

load_dotenv()

SECRET_KEY = os.getenv("JWT_SECRET")
ALGORITHM = "HS256"
TOKEN_EXPIRE = 60 * 24

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password.encode("utf-8")[:72])


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def hash_ai_api_key(apiKey: str) -> str:
    return pwd_context.hash(apiKey.encode("utf-8")[:72])


def verify_ai_api_key(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_access_token(user_id: str, email: str) -> str:
    exp_at = datetime.now(timezone.utc) + timedelta(minutes=TOKEN_EXPIRE)
    payload = {
        "sub": str(user_id),
        "email": email,
        "exp_at": exp_at.isoformat(),
        "exp": int(exp_at.timestamp()),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return {
            "sub": payload.get("sub"),
            "email": payload.get("email"),
            "exp_at": payload.get("exp_at"),
        }
    except JWTError:
        return None
