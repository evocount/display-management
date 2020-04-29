from typing import Optional
from pydantic import BaseModel
from ..rotation import Rotation


class CRTCConfig(BaseModel):
    crtc: Optional[int]
    x: Optional[int]
    y: Optional[int]
    mode: Optional[int]
    rotation: Optional[Rotation]

    class Config:
        use_enum_values = True
