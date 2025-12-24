from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.websockets.manager import ConnectionManager

router = APIRouter()
manager = ConnectionManager()

@router.websocket("/ws/trees/{tree_id}")
async def tree_websocket(websocket: WebSocket, tree_id: str):
    await manager.connect(tree_id, websocket)

    try:
        while True:
            data = await websocket.receive_json()

            await manager.broadcast(tree_id, {
                "type": "TEST_MESSAGE",
                "treeId": tree_id,
                "payload": data
            })
            
    except WebSocketDisconnect:
        manager.disconnect(tree_id, websocket)