from pydantic import BaseModel


class ModeInfo(BaseModel):
    id: int
    width: int
    height: int
    refresh_rate: float
