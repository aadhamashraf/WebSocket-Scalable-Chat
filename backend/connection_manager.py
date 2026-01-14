from fastapi import WebSocket
from typing import Dict, Set, Optional
import logging
from models import Message, User
import json

logger = logging.getLogger(__name__)


class ConnectionManager:
    """
    Manages WebSocket connections for the chat application.
    
    This class handles:
    - Tracking active connections per room
    - User session management
    - Broadcasting messages to room members
    - Connection lifecycle (connect/disconnect)
    """
    
    def __init__(self):
        # Maps room_id -> set of WebSocket connections
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        
        # Maps WebSocket -> User info
        self.user_sessions: Dict[WebSocket, User] = {}
        
        # Maps room_id -> set of user_ids (for tracking unique users)
        self.room_members: Dict[str, Set[str]] = {}
    
    async def connect(self, websocket: WebSocket, user: User, room_id: str):
        """
        Accept a new WebSocket connection and add it to a room.
        
        Args:
            websocket: The WebSocket connection
            user: User information
            room_id: ID of the room to join
        """
        await websocket.accept()
        
        # Initialize room if it doesn't exist
        if room_id not in self.active_connections:
            self.active_connections[room_id] = set()
            self.room_members[room_id] = set()
        
        # Add connection to room
        self.active_connections[room_id].add(websocket)
        self.room_members[room_id].add(user.id)
        
        # Store user session
        user.current_room = room_id
        self.user_sessions[websocket] = user
        
        logger.info(f"User {user.username} connected to room {room_id}")
    
    def disconnect(self, websocket: WebSocket):
        """
        Remove a WebSocket connection and clean up associated data.
        
        Args:
            websocket: The WebSocket connection to remove
        """
        if websocket not in self.user_sessions:
            return
        
        user = self.user_sessions[websocket]
        room_id = user.current_room
        
        if room_id and room_id in self.active_connections:
            # Remove connection from room
            self.active_connections[room_id].discard(websocket)
            self.room_members[room_id].discard(user.id)
            
            # Clean up empty rooms
            if not self.active_connections[room_id]:
                del self.active_connections[room_id]
                del self.room_members[room_id]
        
        # Remove user session
        del self.user_sessions[websocket]
        
        logger.info(f"User {user.username} disconnected from room {room_id}")
    
    async def broadcast_to_room(self, room_id: str, message: Message):
        """
        Send a message to all connections in a specific room.
        
        Args:
            room_id: ID of the room
            message: Message to broadcast
        """
        if room_id not in self.active_connections:
            logger.warning(f"Attempted to broadcast to non-existent room: {room_id}")
            return
        
        # Convert message to JSON
        message_json = message.model_dump_json()
        
        # Send to all connections in the room
        disconnected = set()
        for connection in self.active_connections[room_id]:
            try:
                await connection.send_text(message_json)
            except Exception as e:
                logger.error(f"Error sending message: {e}")
                disconnected.add(connection)
        
        # Clean up any disconnected clients
        for connection in disconnected:
            self.disconnect(connection)
    
    def get_room_member_count(self, room_id: str) -> int:
        """
        Get the number of unique users in a room.
        
        Args:
            room_id: ID of the room
            
        Returns:
            Number of unique members
        """
        return len(self.room_members.get(room_id, set()))
    
    def get_user_info(self, websocket: WebSocket) -> Optional[User]:
        """
        Get user information for a WebSocket connection.
        
        Args:
            websocket: The WebSocket connection
            
        Returns:
            User object or None if not found
        """
        return self.user_sessions.get(websocket)
    
    def get_all_rooms(self) -> Dict[str, int]:
        """
        Get all active rooms and their member counts.
        
        Returns:
            Dictionary mapping room_id to member count
        """
        return {
            room_id: len(members) 
            for room_id, members in self.room_members.items()
        }
