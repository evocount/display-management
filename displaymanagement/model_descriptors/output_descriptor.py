from pydantic import BaseModel
from typing import List, Optional
from .edid_descriptor import EDIDDescriptor
from ..rotation import Rotation


class OutputDescriptor(BaseModel):
    id: int
    name: str
    current_mode_id: Optional[int]
    available_mode_ids: List[int]
    is_connected: bool
    x: Optional[int]
    y: Optional[int]
    rotation: Optional[Rotation]
    edid: Optional[EDIDDescriptor]

    class Config:
        use_enum_values = True
