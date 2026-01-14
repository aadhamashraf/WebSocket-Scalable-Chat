import redis.asyncio as redis
import json
import asyncio
import logging
from typing import Callable, Optional
from models import Message

logger = logging.getLogger(__name__)


class RedisManager:
    """
    Manages Redis pub/sub for distributed message broadcasting.
    
    This enables horizontal scaling by allowing multiple FastAPI instances
    to share messages across rooms through Redis pub/sub channels.
    """
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        """
        Initialize Redis manager.
        
        Args:
            redis_url: Redis connection URL
        """
        self.redis_url = redis_url
        self.redis_client: Optional[redis.Redis] = None
        self.pubsub: Optional[redis.client.PubSub] = None
        self.listener_task: Optional[asyncio.Task] = None
        self.message_handler: Optional[Callable] = None
    
    async def connect(self):
        """Establish connection to Redis"""
        try:
            self.redis_client = await redis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True
            )
            self.pubsub = self.redis_client.pubsub()
            logger.info("Connected to Redis successfully")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise
    
    async def disconnect(self):
        """Close Redis connection and stop listener"""
        if self.listener_task:
            self.listener_task.cancel()
            try:
                await self.listener_task
            except asyncio.CancelledError:
                pass
        
        if self.pubsub:
            await self.pubsub.close()
        
        if self.redis_client:
            await self.redis_client.close()
        
        logger.info("Disconnected from Redis")
    
    async def publish_message(self, room_id: str, message: Message):
        """
        Publish a message to a room's Redis channel.
        
        Args:
            room_id: ID of the room
            message: Message to publish
        """
        if not self.redis_client:
            logger.error("Redis client not connected")
            return
        
        try:
            channel = f"room:{room_id}"
            message_json = message.model_dump_json()
            await self.redis_client.publish(channel, message_json)
            logger.debug(f"Published message to {channel}")
        except Exception as e:
            logger.error(f"Error publishing message: {e}")
    
    async def subscribe_to_room(self, room_id: str):
        """
        Subscribe to a room's Redis channel.
        
        Args:
            room_id: ID of the room to subscribe to
        """
        if not self.pubsub:
            logger.error("PubSub not initialized")
            return
        
        try:
            channel = f"room:{room_id}"
            await self.pubsub.subscribe(channel)
            logger.info(f"Subscribed to {channel}")
        except Exception as e:
            logger.error(f"Error subscribing to room: {e}")
    
    async def unsubscribe_from_room(self, room_id: str):
        """
        Unsubscribe from a room's Redis channel.
        
        Args:
            room_id: ID of the room to unsubscribe from
        """
        if not self.pubsub:
            return
        
        try:
            channel = f"room:{room_id}"
            await self.pubsub.unsubscribe(channel)
            logger.info(f"Unsubscribed from {channel}")
        except Exception as e:
            logger.error(f"Error unsubscribing from room: {e}")
    
    def set_message_handler(self, handler: Callable):
        """
        Set the callback function for handling incoming messages.
        
        Args:
            handler: Async function that takes (room_id, message) as arguments
        """
        self.message_handler = handler
    
    async def start_listening(self):
        """
        Start listening for messages on subscribed channels.
        This runs in the background and calls the message handler for each message.
        """
        if not self.pubsub:
            logger.error("PubSub not initialized")
            return
        
        logger.info("Started Redis listener")
        
        try:
            async for message in self.pubsub.listen():
                if message["type"] == "message":
                    try:
                        # Extract room_id from channel name (format: "room:room_id")
                        channel = message["channel"]
                        room_id = channel.split(":", 1)[1]
                        
                        # Parse message
                        message_data = json.loads(message["data"])
                        msg = Message(**message_data)
                        
                        # Call handler if set
                        if self.message_handler:
                            await self.message_handler(room_id, msg)
                        
                    except Exception as e:
                        logger.error(f"Error processing message: {e}")
        except asyncio.CancelledError:
            logger.info("Redis listener cancelled")
        except Exception as e:
            logger.error(f"Error in Redis listener: {e}")
    
    def start_listener_task(self):
        """Start the listener as a background task"""
        if not self.listener_task or self.listener_task.done():
            self.listener_task = asyncio.create_task(self.start_listening())
