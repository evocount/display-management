from pydantic import BaseModel
from typing import List
from .screen_descriptor import ScreenDescriptor


class DisplayDescriptor(BaseModel):
    id: str
    screen_count: int
    screens: List[ScreenDescriptor]
