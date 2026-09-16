from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from .database import get_db
from .models import User
from .security import decode_access_token

bearer = HTTPBearer(auto_error=True)

async def current_user(
    creds: HTTPAuthorizationCredentials = Depends(bearer),
    db: AsyncSession = Depends(get_db),
):
    user_id = decode_access_token(creds.credentials)
    user = await db.get(User, user_id)
    if not user or not user.is_active:
        from fastapi import HTTPException
        raise HTTPException(401, "User not found or inactive")
    return user
