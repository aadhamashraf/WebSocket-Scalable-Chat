from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class MessageType(str, Enum):
    """Types of messages that can be sent through the WebSocket"""
    CHAT = "chat"
    JOIN = "join"
    LEAVE = "leave"
    TYPING = "typing"
    SYSTEM = "system"


class Message(BaseModel):
    """
    Represents a chat message.
    
    Attributes:
        user_id: Unique identifier for the user
        username: Display name of the user
        room_id: ID of the room where the message was sent
        content: The actual message content
        message_type: Type of message (chat, join, leave, etc.)
        timestamp: When the message was created
    """
    user_id: str
    username: str
    room_id: str
    content: str
    message_type: MessageType = MessageType.CHAT
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class Room(BaseModel):
    """
    Represents a chat room.
    
    Attributes:
        id: Unique identifier for the room
        name: Display name of the room
        created_at: When the room was created
        member_count: Number of active members (computed at runtime)
    """
    id: str
    name: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    member_count: int = 0

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class User(BaseModel):
    """
    Represents a user in the chat system.
    
    Attributes:
        id: Unique identifier for the user
        username: Display name
        current_room: ID of the room the user is currently in
    """
    id: str
    username: str
    current_room: Optional[str] = None


class JoinRoomRequest(BaseModel):
    """Request model for joining a room"""
    username: str
    room_id: str


class CreateRoomRequest(BaseModel):
    """Request model for creating a new room"""
    name: str
