# WebSocket Scalable Chat

A production-ready, scalable multi-room WebSocket chat application built with FastAPI, Redis pub/sub, and React.

## Features

- **Real-time Messaging**: Instant message delivery using WebSocket connections
- **Multi-Room Support**: Create and join multiple chat rooms
- **Horizontal Scalability**: Redis pub/sub enables multiple backend instances
- **Auto-Reconnection**: Automatic WebSocket reconnection on connection loss
- **User Presence**: See who's online in each room
- **Modern UI**: Premium dark theme with glassmorphism and smooth animations
- **Responsive Design**: Works seamlessly on desktop and mobile devices

## Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Client 1  │────▶│  FastAPI 1  │────▶│             │
└─────────────┘     └─────────────┘     │             │
                                        │   Redis     │
┌─────────────┐     ┌─────────────┐     │   Pub/Sub   │
│   Client 2  │────▶│  FastAPI 2  │────▶│             │
└─────────────┘     └─────────────┘     │             │
                                        └─────────────┘
```

The application uses WebSocket for real-time bidirectional communication. Redis pub/sub allows multiple FastAPI instances to share messages, enabling horizontal scaling.

## Tech Stack

### Backend
- **FastAPI**: Modern Python web framework
- **Redis**: In-memory data store for pub/sub messaging
- **WebSockets**: Real-time communication protocol
- **Pydantic**: Data validation and settings management

### Frontend
- **React**: UI library
- **TypeScript**: Type-safe JavaScript
- **Vite**: Fast build tool and dev server
- **CSS3**: Modern styling with custom properties

## Prerequisites

- Python 3.8+
- Node.js 16+
- Redis 6+
- npm or yarn

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/aadhamashraf WebSocket-Scalable-Chat.git
cd websocket-chat
```

### 2. Set up the backend

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
copy .env.example .env
```

### 3. Set up the frontend

```bash
cd frontend

# Install dependencies
npm install

# Copy environment file
copy .env.example .env
```

### 4. Start Redis

Using Docker:
```bash
docker run -d -p 6379:6379 redis:alpine
```

Or install Redis locally and start it:
```bash
redis-server
```

## Running the Application

### Development Mode

**Terminal 1 - Backend:**
```bash
cd backend
uvicorn main:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

The application will be available at:
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Testing Scalability

To test horizontal scaling, run multiple backend instances:

**Terminal 1:**
```bash
uvicorn main:app --port 8000
```

**Terminal 2:**
```bash
uvicorn main:app --port 8001
```

Configure a load balancer (like nginx) to distribute traffic between instances. All instances will share messages through Redis pub/sub.

## Project Structure

```
Project #5/
├── backend/
│   ├── main.py                 # FastAPI application entry point
│   ├── models.py               # Pydantic models
│   ├── connection_manager.py  # WebSocket connection manager
│   ├── redis_manager.py        # Redis pub/sub manager
│   ├── requirements.txt        # Python dependencies
│   └── .env                    # Environment configuration
│
└── frontend/
    ├── src/
    │   ├── components/
    │   │   ├── Login.tsx       # Login screen
    │   │   ├── RoomSelector.tsx # Room list and creation
    │   │   └── ChatRoom.tsx    # Chat interface
    │   ├── hooks/
    │   │   └── useWebSocket.ts # WebSocket hook
    │   ├── api.ts              # API client
    │   ├── types.ts            # TypeScript types
    │   ├── App.tsx             # Main app component
    │   ├── main.tsx            # React entry point
    │   └── index.css           # Global styles
    ├── index.html
    ├── package.json
    └── vite.config.ts
```

## API Endpoints

### REST API

- `GET /` - Health check
- `GET /api/rooms` - Get all chat rooms
- `POST /api/rooms` - Create a new room
  ```json
  {
    "name": "Room Name"
  }
  ```

### WebSocket

- `WS /ws/{room_id}?username={username}` - Connect to a chat room

**Message Format:**
```json
{
  "user_id": "uuid",
  "username": "John Doe",
  "room_id": "general",
  "content": "Hello, world!",
  "message_type": "chat",
  "timestamp": "2026-01-13T19:51:17.000Z"
}
```

## Configuration

### Backend (.env)

```env
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
APP_NAME=WebSocket Chat
DEBUG=True
```

### Frontend (.env)

```env
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000
```

## Features in Detail

### Real-time Messaging
Messages are instantly delivered to all connected clients in the same room using WebSocket connections.

### Room Management
- Default rooms: General, Random, Tech Talk
- Create custom rooms dynamically
- See member count for each room
- Auto-refresh room list every 5 seconds

### Connection Management
- Automatic reconnection on connection loss
- Up to 5 reconnection attempts with 2-second delay
- Connection status indicators
- Graceful handling of disconnections

### Scalability
Redis pub/sub enables running multiple backend instances. When a message is sent to any instance, it's published to Redis and broadcast to all instances, ensuring all connected clients receive it regardless of which instance they're connected to.

## Production Deployment

### Backend

1. Set `DEBUG=False` in `.env`
2. Use a production ASGI server like Gunicorn with Uvicorn workers:
   ```bash
   gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
   ```
3. Set up Redis with persistence and replication
4. Use environment variables for sensitive configuration
5. Enable HTTPS/WSS

### Frontend

1. Build the production bundle:
   ```bash
   npm run build
   ```
2. Serve the `dist` folder with a web server (nginx, Apache, etc.)
3. Update `.env` with production API URLs
4. Enable HTTPS

### Load Balancing

Configure nginx to load balance between backend instances:

```nginx
upstream backend {
    server localhost:8000;
    server localhost:8001;
}

server {
    location / {
        proxy_pass http://backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

## Troubleshooting

### WebSocket connection fails
- Ensure Redis is running
- Check CORS configuration
- Verify WebSocket URL format

### Messages not syncing across instances
- Confirm Redis pub/sub is working
- Check Redis connection in logs
- Verify all instances use the same Redis server

### Frontend can't connect to backend
- Check API URL in frontend `.env`
- Ensure backend is running
- Verify CORS origins include frontend URL

## License

MIT

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
