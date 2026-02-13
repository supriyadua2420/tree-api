from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from pydantic import ValidationError, parse_obj_as
from typing import Union
import time
import uuid

from app.websockets.manager import ConnectionManager
from app.database import db
from app.websockets.events import (
    NodeMoveEvent,
    NodeLabelUpdateEvent,
)

nodes_collection = db.get_collection("nodes")

router = APIRouter()
manager = ConnectionManager()

TreeEvent = Union[
    NodeMoveEvent,
    NodeLabelUpdateEvent,
]

@router.websocket("/ws/trees/{tree_id}/{client_id}")
async def tree_websocket(websocket: WebSocket, tree_id: str, client_id: str):
    await manager.connect(tree_id, client_id, websocket)

    try:
        while True:
            raw = await websocket.receive_json()
            print("Received raw:", raw)


            try:
                event = parse_obj_as(TreeEvent, raw)
            except ValidationError as e:
                print("Validation failed:", e)
                await websocket.send_json({
                    "type": "ERROR",
                    "message": "Invalid event format",
                    "details": e.errors(),
                })
                continue
            
            node_id = event.payload.nodeId
            client_version = getattr(event.payload, "version", 1)

            node = await nodes_collection.find_one({"id": node_id})
            if not node:
                await websocket.send_json({
                    "type": "ERROR",
                    "message": f"Node {node_id} not found",
                })
                continue

            server_version = node.get("version", 1)

            if client_version < server_version:
                await websocket.send_json({
                    "type": "ERROR",
                    "message": "Version conflict",
                    "serverVersion": server_version,
                })
                continue

            # updated_node = {**node, **event.payload.model_dump(), "version": server_version + 1}
            # await nodes_collection.replace_one({"id": node_id}, updated_node)

            payload = event.payload

            updated_node = {
                **node,
                "label": getattr(payload, "label", node["label"]),
                "x": getattr(payload, "x", node.get("x")),
                "y": getattr(payload, "y", node.get("y")),
                "parent_id": getattr(payload, "parentId", node.get("parent_id")),
                "version": server_version + 1,
            }

            print("Looking for node:", node_id)
            await nodes_collection.replace_one({"id": node_id}, updated_node)
            print("Found node:", node)


            event_dict = event.dict()
            event_dict['serverTS'] = time.time()
            event_dict['eventId'] = str(uuid.uuid4())
            event_dict['node'] = updated_node
            event_dict['type'] = event.type
            await manager.broadcast(tree_id, event_dict)
                                                                 
    except WebSocketDisconnect:
        manager.disconnect(tree_id, client_id)
