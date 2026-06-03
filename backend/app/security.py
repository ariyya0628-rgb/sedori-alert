from datetime import datetime, timedelta, timezone
import warnings

from jose import jwt
from jose.exceptions import JWTError
from passlib.context import CryptContext

from app.config import settings


pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return pwd_context.verify(password, password_hash)


def create_access_token(user_id: int) -> str:
    expires_at = datetime.now(timezone.utc) + timedelta(days=7)
    payload = {"sub": str(user_id), "exp": expires_at}
    return jwt.encode(payload, settings.jwt_secret, algorithm="HS256")


def decode_access_token(token: str) -> int | None:
    try:
        with warnings.catch_warnings():
            warnings.filterwarnings(
                "ignore",
                message=r"datetime\.datetime\.utcnow\(\) is deprecated.*",
                category=DeprecationWarning,
            )
            payload = jwt.decode(token, settings.jwt_secret, algorithms=["HS256"])
        subject = payload.get("sub")
        return int(subject) if subject else None
    except (JWTError, ValueError):
        return None
