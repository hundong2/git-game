"""WebSocket connection manager for real-time updates"""

from typing import Dict, List
from fastapi import WebSocket
import json
import asyncio

class WebSocketManager:
    """Manages WebSocket connections for real-time game updates"""
    
    def __init__(self):
        # Store active connections by session_id
        self.active_connections: Dict[str, List[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, session_id: str):
        """Accept new WebSocket connection"""
        await websocket.accept()
        
        if session_id not in self.active_connections:
            self.active_connections[session_id] = []
        
        self.active_connections[session_id].append(websocket)
        
        # Send welcome message
        await websocket.send_text(json.dumps({
            "type": "connected",
            "message": "Connected to game session",
            "session_id": session_id
        }))
    
    def disconnect(self, websocket: WebSocket, session_id: str):
        """Remove WebSocket connection"""
        if session_id in self.active_connections:
            if websocket in self.active_connections[session_id]:
                self.active_connections[session_id].remove(websocket)
            
            # Clean up empty session
            if not self.active_connections[session_id]:
                del self.active_connections[session_id]
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        """Send message to specific WebSocket"""
        try:
            await websocket.send_text(message)
        except Exception as e:
            print(f"Error sending personal message: {e}")
    
    async def broadcast_to_session(self, session_id: str, message: Dict):
        """Broadcast message to all connections in a session"""
        if session_id not in self.active_connections:
            return
        
        message_text = json.dumps(message)
        
        # Send to all connections in the session
        disconnected = []
        for connection in self.active_connections[session_id]:
            try:
                await connection.send_text(message_text)
            except Exception as e:
                print(f"Error broadcasting to session {session_id}: {e}")
                disconnected.append(connection)
        
        # Clean up disconnected connections
        for connection in disconnected:
            self.disconnect(connection, session_id)
    
    async def broadcast_global(self, message: Dict):
        """Broadcast message to all connected clients"""
        message_text = json.dumps(message)
        
        for session_id in list(self.active_connections.keys()):
            await self.broadcast_to_session(session_id, message)
    
    def get_session_connection_count(self, session_id: str) -> int:
        """Get number of active connections for a session"""
        return len(self.active_connections.get(session_id, []))
    
    def get_total_connections(self) -> int:
        """Get total number of active connections"""
        return sum(len(connections) for connections in self.active_connections.values())
    
    async def send_teammate_simulation(self, session_id: str):
        """Send teammate activity simulation"""
        teammate_actions = [
            {"type": "teammate_commit", "teammate": "alice", "action": "Added new feature"},
            {"type": "teammate_push", "teammate": "bob", "action": "Pushed to feature branch"},
            {"type": "teammate_merge", "teammate": "charlie", "action": "Merged PR #123"}, 
            {"type": "teammate_rebase", "teammate": "diana", "action": "Rebased feature branch"}
        ]
        
        import random
        action = random.choice(teammate_actions)
        
        await self.broadcast_to_session(session_id, {
            "type": "teammate_activity",
            "data": action,
            "timestamp": asyncio.get_event_loop().time()
        })
