from pydantic import BaseModel
from typing import Optional

class Node(BaseModel):
    id: Optional[str]
    label: str
    parent_id: Optional[str] = None
    x: float = 0.0
    y: float = 0.0

class NodeUpdate(BaseModel):
    label: Optional[str] = None
    parent_id: Optional[str] = None
    x: Optional[float] = None
    y: Optional[float] = None
