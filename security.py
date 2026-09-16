import hashlib, secrets, uuid
from datetime import datetime, timedelta, timezone
import jwt
from pwdlib import PasswordHash
from fastapi import HTTPException, status
from .config import settings

password_hash = PasswordHash.recommended()

def hash_password(password: str) -> str:
    return password_hash.hash(password)

def verify_password(password: str, stored: str) -> bool:
    return password_hash.verify(password, stored)

def create_access_token(user_id: uuid.UUID) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),
        "type": "access",
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=settings.access_token_minutes)).timestamp()),
        "jti": str(uuid.uuid4()),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)

def decode_access_token(token: str) -> uuid.UUID:
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        if payload.get("type") != "access":
            raise ValueError()
        return uuid.UUID(payload["sub"])
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired access token")

def new_refresh_token() -> str:
    return secrets.token_urlsafe(64)

def hash_refresh_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()
