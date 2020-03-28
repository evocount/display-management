from pydantic import BaseModel
from typing import List, Optional
from .output_descriptor import OutputDescriptor
from .screen_size import ScreenSize
from .mode_info import ModeInfo


class ScreenSizeRange(BaseModel):
    min_width: int
    max_width: int
    min_height: int
    max_height: int


class ScreenDescriptor(BaseModel):
    id: int
    size: Optional[ScreenSize]
    outputs: List[OutputDescriptor]
    modes: List[ModeInfo]
    size_range: ScreenSizeRange
