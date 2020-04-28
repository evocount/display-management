from typing import List
from pydantic import BaseModel
from ..rotation import Rotation


class CRTCInfo(BaseModel):
    x: int
    y: int
    width: int
    height: int
    mode_id: int
    rotation: Rotation
    outputs: List[int]
    possible_outputs: List[int]

    class Config:
        use_enum_values = True
