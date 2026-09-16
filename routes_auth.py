from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from .database import get_db
from .models import User, Session
from .schemas import RegisterIn, LoginIn, RefreshIn, TokenOut
from .security import *
from .deps import current_user

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=TokenOut)
async def register(data: RegisterIn, request: Request, db: AsyncSession = Depends(get_db)):
    existing = await db.scalar(select(User).where(User.username == data.username.lower()))
    if existing:
        raise HTTPException(409, "Username already exists")
    user = User(
        username=data.username.lower(),
        display_name=data.display_name,
        password_hash=hash_password(data.password),
    )
    db.add(user)
    await db.flush()
    refresh = new_refresh_token()
    session = Session(
        user_id=user.id,
        refresh_token_hash=hash_refresh_token(refresh),
        device_identifier=request.headers.get("user-agent", "unknown")[:200],
        expires_at=datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_days),
    )
    db.add(session)
    await db.commit()
    return TokenOut(access_token=create_access_token(user.id), refresh_token=refresh)

@router.post("/login", response_model=TokenOut)
async def login(data: LoginIn, db: AsyncSession = Depends(get_db)):
    user = await db.scalar(select(User).where(User.username == data.username.lower()))
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(401, "Invalid username or password")
    refresh = new_refresh_token()
    session = Session(
        user_id=user.id,
        refresh_token_hash=hash_refresh_token(refresh),
        device_identifier=data.device_identifier,
        expires_at=datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_days),
    )
    db.add(session)
    user.last_seen = datetime.now(timezone.utc)
    await db.commit()
    return TokenOut(access_token=create_access_token(user.id), refresh_token=refresh)

@router.post("/refresh", response_model=TokenOut)
async def refresh(data: RefreshIn, db: AsyncSession = Depends(get_db)):
    digest = hash_refresh_token(data.refresh_token)
    session = await db.scalar(select(Session).where(Session.refresh_token_hash == digest))
    now = datetime.now(timezone.utc)
    if not session or session.revoked or session.expires_at <= now:
        raise HTTPException(401, "Invalid refresh session")
    session.revoked = True
    new_refresh = new_refresh_token()
    replacement = Session(
        user_id=session.user_id,
        refresh_token_hash=hash_refresh_token(new_refresh),
        device_identifier=session.device_identifier,
        expires_at=now + timedelta(days=settings.refresh_token_days),
    )
    db.add(replacement)
    await db.commit()
    return TokenOut(access_token=create_access_token(session.user_id), refresh_token=new_refresh)

@router.post("/logout")
async def logout(user=Depends(current_user), db: AsyncSession = Depends(get_db)):
    sessions = (await db.scalars(select(Session).where(Session.user_id == user.id, Session.revoked == False))).all()
    for s in sessions:
        s.revoked = True
    await db.commit()
    return {"ok": True}
