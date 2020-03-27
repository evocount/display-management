from pydantic import BaseModel
from typing import List, Optional


class OutputDescriptor(BaseModel):
    id: int
    name: str
    current_mode_id: Optional[int]
    available_mode_ids: List[int]
    is_connected: bool
