from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import os
from dotenv import load_dotenv
import uuid
from typing import List

from models import (
    Message, Room, User, MessageType, 
    JoinRoomRequest, CreateRoomRequest
)
from connection_manager import ConnectionManager
from redis_manager import RedisManager

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize managers
connection_manager = ConnectionManager()
redis_manager = RedisManager(
    redis_url=f"redis://{os.getenv('REDIS_HOST', 'localhost')}:{os.getenv('REDIS_PORT', '6379')}"
)

# Store room metadata (in production, use a database)
rooms_db: dict[str, Room] = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Handles startup and shutdown events.
    """
    # Startup
    logger.info("Starting up application...")
    await redis_manager.connect()
    
    # Set up message handler for Redis pub/sub
    async def handle_redis_message(room_id: str, message: Message):
        """Handle messages received from Redis pub/sub"""
        await connection_manager.broadcast_to_room(room_id, message)
    
    redis_manager.set_message_handler(handle_redis_message)
    redis_manager.start_listener_task()
    
    # Create default rooms
    default_rooms = [
        {"id": "general", "name": "General"},
        {"id": "random", "name": "Random"},
        {"id": "tech", "name": "Tech Talk"}
    ]
    
    for room_data in default_rooms:
        rooms_db[room_data["id"]] = Room(
            id=room_data["id"],
            name=room_data["name"]
        )
    
    logger.info("Application started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down application...")
    await redis_manager.disconnect()
    logger.info("Application shut down successfully")


# Create FastAPI app
app = FastAPI(
    title="WebSocket Chat API",
    description="Scalable multi-room chat using WebSockets and Redis pub/sub",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
origins = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "online",
        "message": "WebSocket Chat API is running"
    }


@app.get("/api/rooms", response_model=List[Room])
async def get_rooms():
    """
    Get all available chat rooms.
    
    Returns:
        List of rooms with their current member counts
    """
    room_counts = connection_manager.get_all_rooms()
    
    rooms = []
    for room_id, room in rooms_db.items():
        room_copy = room.model_copy()
        room_copy.member_count = room_counts.get(room_id, 0)
        rooms.append(room_copy)
    
    return rooms


@app.post("/api/rooms", response_model=Room)
async def create_room(request: CreateRoomRequest):
    """
    Create a new chat room.
    
    Args:
        request: Room creation request with name
        
    Returns:
        The created room
    """
    room_id = str(uuid.uuid4())
    
    room = Room(
        id=room_id,
        name=request.name
    )
    
    rooms_db[room_id] = room
    logger.info(f"Created new room: {room.name} ({room_id})")
    
    return room


@app.websocket("/ws/{room_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: str):
    """
    WebSocket endpoint for real-time chat.
    
    Args:
        websocket: WebSocket connection
        room_id: ID of the room to join
    """
    # Get user info from query params
    username = websocket.query_params.get("username", "Anonymous")
    user_id = str(uuid.uuid4())
    
    user = User(
        id=user_id,
        username=username,
        current_room=room_id
    )
    
    # Verify room exists
    if room_id not in rooms_db:
        await websocket.close(code=1008, reason="Room not found")
        return
    
    # Connect user
    await connection_manager.connect(websocket, user, room_id)
    
    # Subscribe to Redis channel for this room
    await redis_manager.subscribe_to_room(room_id)
    
    # Send join notification
    join_message = Message(
        user_id=user_id,
        username=username,
        room_id=room_id,
        content=f"{username} joined the room",
        message_type=MessageType.JOIN
    )
    await redis_manager.publish_message(room_id, join_message)
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            
            # Create message object
            message = Message(
                user_id=user_id,
                username=username,
                room_id=room_id,
                content=data,
                message_type=MessageType.CHAT
            )
            
            # Publish to Redis (will be broadcast to all instances)
            await redis_manager.publish_message(room_id, message)
            
    except WebSocketDisconnect:
        # Handle disconnect
        connection_manager.disconnect(websocket)
        
        # Send leave notification
        leave_message = Message(
            user_id=user_id,
            username=username,
            room_id=room_id,
            content=f"{username} left the room",
            message_type=MessageType.LEAVE
        )
        await redis_manager.publish_message(room_id, leave_message)
        
        logger.info(f"User {username} disconnected from room {room_id}")
    
    except Exception as e:
        logger.error(f"Error in WebSocket connection: {e}")
        connection_manager.disconnect(websocket)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
