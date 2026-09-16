import uuid
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from sqlalchemy import select
from .database import SessionLocal
from .models import ConversationMember, Message
from .security import decode_access_token
from datetime import datetime, timezone

router = APIRouter(tags=["websocket"])

class ConnectionManager:
    def __init__(self):
        self.connections: dict[uuid.UUID, set[WebSocket]] = {}

    async def connect(self, user_id, ws):
        await ws.accept()
        self.connections.setdefault(user_id, set()).add(ws)

    def disconnect(self, user_id, ws):
        self.connections.get(user_id, set()).discard(ws)

    async def send_user(self, user_id, payload):
        for ws in list(self.connections.get(user_id, set())):
            try:
                await ws.send_json(payload)
            except Exception:
                self.disconnect(user_id, ws)

manager = ConnectionManager()

@router.websocket("/ws")
async def websocket_endpoint(ws: WebSocket, token: str | None = None):
    if not token:
        await ws.close(code=1008)
        return
    try:
        user_id = decode_access_token(token)
    except Exception:
        await ws.close(code=1008)
        return

    await manager.connect(user_id, ws)
    try:
        await ws.send_json({"type": "connected"})
        while True:
            data = await ws.receive_json()
            action = data.get("type")
            if action == "ping":
                await ws.send_json({"type": "pong"})
                continue

            if action != "send_message":
                await ws.send_json({"type": "error", "detail": "Unsupported action"})
                continue

            conversation_id = uuid.UUID(data["conversation_id"])
            body = str(data["body"])
            if not body or len(body) > 10000:
                await ws.send_json({"type": "error", "detail": "Invalid message"})
                continue

            async with SessionLocal() as db:
                member = await db.scalar(select(ConversationMember).where(
                    ConversationMember.conversation_id == conversation_id,
                    ConversationMember.user_id == user_id
                ))
                if not member:
                    await ws.send_json({"type": "error", "detail": "Not authorized"})
                    continue

                msg = Message(conversation_id=conversation_id, sender_id=user_id, body=body)
                db.add(msg)
                await db.commit()
                await db.refresh(msg)

                members = (await db.scalars(select(ConversationMember).where(
                    ConversationMember.conversation_id == conversation_id
                ))).all()

                payload = {
                    "type": "message",
                    "id": str(msg.id),
                    "conversation_id": str(conversation_id),
                    "sender_id": str(user_id),
                    "body": body,
                    "created_at": msg.created_at.isoformat(),
                }

                for member in members:
                    await manager.send_user(member.user_id, payload)
    except WebSocketDisconnect:
        manager.disconnect(user_id, ws)
    except Exception:
        manager.disconnect(user_id, ws)
        try:
            await ws.close(code=1011)
        except Exception:
            pass
