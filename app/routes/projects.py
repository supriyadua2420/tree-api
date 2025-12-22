from fastapi import APIRouter
from app.models import Project
from app.database import db

router = APIRouter(prefix="/projects", tags=["projects"])
projects_collection = db.get_collection("projects")

@router.post("/")
async def create_project(project: Project):
    result = await projects_collection.insert_one(project.dict())
    return {"id": str(result.inserted_id)}
