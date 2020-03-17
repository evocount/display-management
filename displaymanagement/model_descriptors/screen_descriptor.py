from pydantic import BaseModel
from typing import List, Optional
from .output_descriptor import OutputDescriptor
from .screen_size import ScreenSize
from .mode_info import ModeInfo


class ScreenDescriptor(BaseModel):
    id: int
    sizes: List[ScreenSize]
    size: Optional[ScreenSize]
    outputs: List[OutputDescriptor]
    modes: List[ModeInfo]
