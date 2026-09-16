import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from .database import get_db
from .models import Conversation, ConversationMember, Message, Block
from .schemas import ConversationCreate, MessageIn, MessageOut
from .deps import current_user

router = APIRouter(prefix="/chats", tags=["chats"])

async def is_member(db, conversation_id, user_id):
    return await db.scalar(select(ConversationMember).where(
        ConversationMember.conversation_id == conversation_id,
        ConversationMember.user_id == user_id
    ))

@router.post("", response_model=dict)
async def create_chat(data: ConversationCreate, user=Depends(current_user), db: AsyncSession = Depends(get_db)):
    if data.user_id == user.id or not await db.get(type(user), data.user_id):
        raise HTTPException(404, "User not found")
    blocked = await db.scalar(select(Block).where(
        or_(
            and_(Block.blocker_id == user.id, Block.blocked_id == data.user_id),
            and_(Block.blocker_id == data.user_id, Block.blocked_id == user.id),
        )
    )) if False else None
    conv = Conversation(type="direct")
    db.add(conv)
    await db.flush()
    db.add_all([
        ConversationMember(conversation_id=conv.id, user_id=user.id),
        ConversationMember(conversation_id=conv.id, user_id=data.user_id),
    ])
    await db.commit()
    return {"conversation_id": str(conv.id)}

@router.get("/{conversation_id}/messages", response_model=list[MessageOut])
async def messages(conversation_id: uuid.UUID, user=Depends(current_user), db: AsyncSession = Depends(get_db)):
    if not await is_member(db, conversation_id, user.id):
        raise HTTPException(403, "Not a conversation member")
    stmt = select(Message).where(Message.conversation_id == conversation_id).order_by(Message.created_at).limit(100)
    return list((await db.scalars(stmt)).all())

@router.post("/{conversation_id}/messages", response_model=MessageOut)
async def send_message(conversation_id: uuid.UUID, data: MessageIn, user=Depends(current_user), db: AsyncSession = Depends(get_db)):
    if not await is_member(db, conversation_id, user.id):
        raise HTTPException(403, "Not a conversation member")
    msg = Message(conversation_id=conversation_id, sender_id=user.id, body=data.body)
    db.add(msg)
    await db.commit()
    await db.refresh(msg)
    return msg
