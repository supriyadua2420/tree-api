from fastapi import FastAPI
from app.routes import nodes
from app.database import db

app = FastAPI()

# Include your nodes router
app.include_router(nodes.router)

@app.get("/")
async def read_root():
    collections = await db.list_collection_names()
    return {"Hello": "World", "collections": collections}
