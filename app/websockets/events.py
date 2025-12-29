from pydantic import BaseModel
from typing import Literal
from typing import Optional
import time
import uuid

class BaseEvent(BaseModel):
    type: str
    treeId: str
    clientId: str
    serverTS: Optional[float] = None
    eventId: Optional[str] = None


class NodeMovePayload(BaseModel):
    nodeId: str
    x: float
    y: float


class NodeLabelUpdatePayload(BaseModel):
    nodeId: str
    label: str


class NodeMoveEvent(BaseEvent):
    type: Literal["NODE_MOVED"]
    payload: NodeMovePayload


class NodeLabelUpdateEvent(BaseEvent):
    type: Literal["NODE_LABEL_UPDATED"]
    payload: NodeLabelUpdatePayload
