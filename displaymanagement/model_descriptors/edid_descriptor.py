from pydantic import BaseModel


class EDIDDescriptor(BaseModel):
    manufacturer: str
    manufacturer_product_code: str
    manufacturer_serial_number: str
    width: float
    height: float
