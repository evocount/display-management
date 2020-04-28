from typing import List
from pydantic import BaseModel


class CRTCInfo(BaseModel):
    x: int
    y: int
    width: int
    height: int
    mode_id: int
    outputs: List[int]
    possible_outputs: List[int]
