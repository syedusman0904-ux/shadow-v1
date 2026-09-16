import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from .database import get_db
from .models import User, Block
from .schemas import UserOut
from .deps import current_user

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/search", response_model=list[UserOut])
async def search(q: str, user=Depends(current_user), db: AsyncSession = Depends(get_db)):
    q = q.strip().lower()
    if not q:
        return []
    stmt = select(User).where(
        User.is_active == True,
        or_(User.username.ilike(f"%{q}%"), User.id.cast(str).ilike(f"%{q}%"))
    ).limit(20)
    return list((await db.scalars(stmt)).all())

@router.get("/{user_id}", response_model=UserOut)
async def profile(user_id: uuid.UUID, user=Depends(current_user), db: AsyncSession = Depends(get_db)):
    target = await db.get(User, user_id)
    if not target:
        raise HTTPException(404, "User not found")
    return target

@router.post("/{user_id}/block")
async def block(user_id: uuid.UUID, user=Depends(current_user), db: AsyncSession = Depends(get_db)):
    if user_id == user.id:
        raise HTTPException(400, "Cannot block yourself")
    if not await db.get(User, user_id):
        raise HTTPException(404, "User not found")
    existing = await db.get(Block, {"blocker_id": user.id, "blocked_id": user_id})
    if not existing:
        db.add(Block(blocker_id=user.id, blocked_id=user_id))
        await db.commit()
    return {"blocked": True}

@router.delete("/{user_id}/block")
async def unblock(user_id: uuid.UUID, user=Depends(current_user), db: AsyncSession = Depends(get_db)):
    existing = await db.get(Block, {"blocker_id": user.id, "blocked_id": user_id})
    if existing:
        await db.delete(existing)
        await db.commit()
    return {"blocked": False}
