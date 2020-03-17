from pydantic import BaseModel


class ScreenSize(BaseModel):
    width: int
    height: int
