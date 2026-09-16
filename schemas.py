import uuid
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

class RegisterIn(BaseModel):
    username: str = Field(min_length=3, max_length=32, pattern=r"^[a-zA-Z0-9_]+$")
    display_name: str = Field(min_length=1, max_length=80)
    password: str = Field(min_length=12, max_length=128)

class LoginIn(BaseModel):
    username: str
    password: str
    device_identifier: str = Field(default="unknown-device", max_length=200)

class RefreshIn(BaseModel):
    refresh_token: str

class TokenOut(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    username: str
    display_name: str
    profile_photo: str | None
    bio: str
    created_at: datetime
    last_seen: datetime

class ConversationCreate(BaseModel):
    user_id: uuid.UUID

class MessageIn(BaseModel):
    body: str = Field(min_length=1, max_length=10000)

class MessageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    conversation_id: uuid.UUID
    sender_id: uuid.UUID
    body: str
    created_at: datetime
    edited_at: datetime | None
    deleted_at: datetime | None
    delivered_at: datetime | None
    read_at: datetime | None
