from pydantic import BaseModel


class EDIDDescriptor(BaseModel):
    manufacturer_id: str
    manufacturer_product_code: str
    manufacturer_serial_number: str
    aspect_ratio: str
