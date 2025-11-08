from fastapi import FastAPI
from app.routes import nodes
from app.database import db
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.include_router(nodes.router)

origins = [
    "http://localhost:5173", 
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def read_root():
    collections = await db.list_collection_names()
    return {"Hello": "World", "collections": collections}
