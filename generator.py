from pydantic import BaseModel
from typing import Literal

class Answers(BaseModel):
    objetivo: Literal["ventas", "leads", "branding", "lanzamiento", "test"]
    publico: str
    estetica: Literal["cinematografica", "iphone", "urbana", "minimal", "deportiva", "cozy"]
    duracion: int
