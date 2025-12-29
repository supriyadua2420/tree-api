from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from pydantic import ValidationError, parse_obj_as
from typing import Union

from app.websockets.manager import ConnectionManager
from app.websockets.events import (
    NodeMoveEvent,
    NodeLabelUpdateEvent,
)

router = APIRouter()
manager = ConnectionManager()

TreeEvent = Union[
    NodeMoveEvent,
    NodeLabelUpdateEvent,
]

@router.websocket("/ws/trees/{tree_id}")
async def tree_websocket(websocket: WebSocket, tree_id: str):
    await manager.connect(tree_id, websocket)

    try:
        while True:
            raw = await websocket.receive_json()

            try:
                event = parse_obj_as(TreeEvent, raw)
            except ValidationError as e:
                await websocket.send_json({
                    "type": "ERROR",
                    "message": "Invalid event format",
                    "details": e.errors(),
                })
                continue

            if event.treeId != tree_id:
                await websocket.send_json({
                    "type": "ERROR",
                    "message": "treeId mismatch",
                })
                continue

            await manager.broadcast(tree_id, event.dict())

    except WebSocketDisconnect:
        manager.disconnect(tree_id, websocket)
