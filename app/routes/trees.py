from fastapi import APIRouter
from app.models import Tree
from app.database import db

router = APIRouter(prefix="/trees", tags=["trees"])
trees_collection = db.get_collection("trees")

@router.post("/")
async def create_tree(tree: Tree):
    result = await trees_collection.insert_one(tree.dict())
    return {"id": str(result.inserted_id)}
