from fastapi import WebSocket
from collections import defaultdict

class ConnectionManager:
    def __init__(self):
        #tree_id -> list of WebSocket connections
        self.active_connections = defaultdict(list)

    async def connect(self, tree_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[tree_id].append(websocket)
    
    async def disconnect(self, tree_id: str, websocket: WebSocket):
        if websocket in self.active_connections[tree_id]:
            self.active_connections[tree_id].remove(websocket)

    async def broadcast(self, tree_id: str, message: dict):
        for websocket in self.active_connections[tree_id]:
            await websocket.send_json(message)