from fastapi import FastAPI
from app.routes import nodes
from app.database import db
from app.websockets import trees
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

from app.websockets.trees import manager
from app.core.redis import redis_client
import asyncio
import json

app = FastAPI()

app.include_router(nodes.router)
app.include_router(trees.router)

origins = os.getenv("CORS_ORIGINS", "").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in origins if origin.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def redis_listener():
    while True:
        try:
            pubsub = redis_client.pubsub()
            await pubsub.subscribe("tree_broadcast")

            async for message in pubsub.listen():
                if message["type"] == "message":
                    data = json.loads(message["data"])

                    tree_id = data["tree_id"]
                    payload = data["payload"]
                    exclude_client_id = data.get("exclude_client_id")

                    await manager.broadcast(
                        tree_id,
                        payload,
                        exclude_client_id=exclude_client_id
                    )

        except Exception as e:
            print("Redis listener error:", e)
            await asyncio.sleep(2)  # small backoff before reconnect

            
@app.on_event("startup")
async def startup_event():
    asyncio.create_task(redis_listener())

@app.get("/")
async def read_root():
    collections = await db.list_collection_names()
    return {"Hello": "World", "collections": collections}
