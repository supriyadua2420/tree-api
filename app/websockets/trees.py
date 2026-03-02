from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from pydantic import ValidationError, parse_obj_as
from typing import Union
import time
import uuid
from app.core.redis import redis_client
import json

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

            # -----------------------------
            # Validate event format
            # -----------------------------
            try:
                event = parse_obj_as(TreeEvent, raw)
            except ValidationError as e:
                await websocket.send_json({
                    "type": "ERROR",
                    "message": "Invalid event format",
                    "details": e.errors(),
                })
                continue

            node_id = str(event.payload.nodeId)
            client_version = getattr(event.payload, "version", None)

            if client_version is None:
                await websocket.send_json({
                    "type": "ERROR",
                    "message": "Missing version",
                })
                continue

            # -----------------------------
            # Atomic optimistic update
            # -----------------------------
            payload_dict = event.payload.model_dump()

            update_fields = {}

            if "label" in payload_dict:
                update_fields["label"] = payload_dict["label"]

            if "x" in payload_dict:
                update_fields["x"] = payload_dict["x"]

            if "y" in payload_dict:
                update_fields["y"] = payload_dict["y"]

            if "parentId" in payload_dict:
                update_fields["parent_id"] = payload_dict["parentId"]

            result = await nodes_collection.update_one(
                {
                    "id": node_id,
                    "tree_id": tree_id,
                    "version": client_version,  # 🔥 version check
                },
                {
                    "$set": update_fields,
                    "$inc": {"version": 1},     # 🔥 atomic increment
                }
            )

            # -----------------------------
            # Version conflict
            # -----------------------------
            if result.matched_count == 0:
                latest = await nodes_collection.find_one(
                    {"id": node_id, "tree_id": tree_id}
                )

                if latest is None:
                    await websocket.send_json({
                        "type": "ERROR",
                        "message": "Node not found"
                    })
                    continue

                latest["_id"] = str(latest["_id"])

                await websocket.send_json({
                    "type": "ERROR",
                    "message": "Version conflict",
                    "serverVersion": latest.get("version", 1),
                    "node": latest,
                })
                continue


            # -----------------------------
            # Fetch updated node
            # -----------------------------
            updated_node = await nodes_collection.find_one(
                {"id": node_id, "tree_id": tree_id}
            )

            updated_node["_id"] = str(updated_node["_id"])

            # -----------------------------
            # Broadcast to all clients
            # -----------------------------
            broadcast_event = {
                "type": event.type,
                "treeId": tree_id,
                "clientId": client_id,
                "eventId": str(uuid.uuid4()),
                "serverTS": time.time(),
                "node": updated_node,
            }

            print("Client connected:", id(websocket))
            print("Broadcasting to", len(manager.active_connections.get(tree_id, {})), "clients")
            await redis_client.publish(
                "tree_broadcast",
                json.dumps({
                    "tree_id": tree_id,
                    "payload": broadcast_event,
                })
            )
    except WebSocketDisconnect:
        await manager.disconnect(tree_id, client_id)
