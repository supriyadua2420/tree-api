from fastapi import WebSocket
from collections import defaultdict

class ConnectionManager:
    def __init__(self):
        #tree_id -> client_id -> WebSocket
        self.active_connections: dict[str, dict[str, WebSocket]] = {} #?

    async def connect(self, tree_id: str, client_id: str, websocket: WebSocket):
        await websocket.accept()
        if tree_id not in self.active_connections:
            self.active_connections[tree_id] = {}

        self.active_connections[tree_id][client_id] = websocket
    
    async def disconnect(self, tree_id: str, client_id: str):
        if tree_id in self.active_connections:
            self.active_connections[tree_id].pop(client_id, None)
            if not self.active_connections[tree_id]:
                del self.active_connections[tree_id]

    async def broadcast(self, tree_id: str, message: dict, exclude_client_id: str | None = None):
        if tree_id not in self.active_connections:
            return

        for client_id, websocket in self.active_connections[tree_id].items():
            if client_id == exclude_client_id:
                continue
            await websocket.send_json(message)
        
