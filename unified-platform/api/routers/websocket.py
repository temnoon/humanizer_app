"""
WebSocket Router
Real-time communication for transformations and updates
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import json
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

# Connection manager for WebSocket clients
class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, session_id: str):
        await websocket.accept()
        self.active_connections[session_id] = websocket
        logger.info(f"WebSocket connected: {session_id}")
    
    def disconnect(self, session_id: str):
        if session_id in self.active_connections:
            del self.active_connections[session_id]
            logger.info(f"WebSocket disconnected: {session_id}")
    
    async def send_message(self, session_id: str, message: dict):
        if session_id in self.active_connections:
            try:
                await self.active_connections[session_id].send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"Failed to send message to {session_id}: {e}")
                self.disconnect(session_id)

manager = ConnectionManager()

@router.websocket("/transformations/{session_id}")
async def transformation_websocket(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for real-time transformation updates"""
    await manager.connect(websocket, session_id)
    
    try:
        while True:
            # Wait for messages from client
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Echo back for now (placeholder)
            await manager.send_message(session_id, {
                "type": "echo",
                "data": message,
                "timestamp": "2024-01-01T00:00:00Z"
            })
            
    except WebSocketDisconnect:
        manager.disconnect(session_id)