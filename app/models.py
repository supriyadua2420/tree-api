from pydantic import BaseModel
from typing import Optional

class Node(BaseModel):
    id: Optional[str]
    label: str
    parent_id: Optional[str] = None
    tree_id: Optional[str] = None
    x: float = 0.0
    y: float = 0.0

class NodeUpdate(BaseModel):
    label: Optional[str] = None
    parent_id: Optional[str] = None
    x: Optional[float] = None
    y: Optional[float] = None

class Tree(BaseModel):
    # id: Optional[str] = Field(default_factory=lambda: gen_id("t_"))
    project_id: Optional[str] = None
    name: Optional[str] = None
    created_at: Optional[str] = None

class Project(BaseModel):
    # id: Optional[str] = Field(default_factory=lambda: gen_id("p_"))
    name: str
    tree_id: Optional[str] = None
    description: Optional[str] = None