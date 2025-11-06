from fastapi import APIRouter
from app.BaseModels import Node
from app.database import db

router = APIRouter(prefix="/nodes", tags=["nodes"])

@router.post("/")
async def create_node(node: Node):
    result = await db.nodes.insert_one(node.dict())
    return {"id": str(result.inserted_id)}

@router.get("/")
async def get_nodes():
    nodes = await db.nodes.find().to_list(100)
    return nodes