from pydantic import BaseModel
from typing import Optional

class Node(BaseModel):
    id: Optional[str]
    label: str
    parent_id: Optional[str]