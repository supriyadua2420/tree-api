from fastapi import APIRouter, HTTPException
from app.models import Node, NodeUpdate
from app.database import db

router = APIRouter(prefix="/nodes", tags=["nodes"])
nodes_collection = db.get_collection("nodes")

@router.post("/")
async def create_node(node: Node):
    result = await nodes_collection.insert_one(node.dict())
    return {"id": str(result.inserted_id)}

@router.get("/")
async def get_nodes(tree_id: str = None):
    q = {}
    if tree_id:
        q["tree_id"] = tree_id
    nodes = await nodes_collection.find(q).to_list(100)
    for node in nodes:
        node["_id"] = str(node["_id"])
    return nodes

@router.delete("/{node_id}")
async def delete_node(node_id: str):
    node = await nodes_collection.find_one({"id": node_id})
    if not node:
        return {"message": "Not found"}

    parent_id = node.get("parent_id")

    await nodes_collection.update_many(
        {"parent_id": node_id},
        {"$set": {"parent_id": parent_id}}
    )
    await nodes_collection.delete_one({"id": node_id})

    return {"message": "Deleted"}

@router.put("/{node_id}")
async def update_node(node_id: str, node: NodeUpdate):
    update_doc = {k: v for k, v in node.dict().items() if v is not None}
    if not update_doc:
        raise HTTPException(status_code=400, detail="No fields provided to update")

    result = await nodes_collection.update_one(
        {"id": node_id},
        {"$set": update_doc}
    )

    return {"status": "updated"}