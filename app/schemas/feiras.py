from pydantic import BaseModel, ConfigDict
from decimal import Decimal
from datetime import date
from typing import Optional 


class FeiraBase(BaseModel):
    """Schema base contendo os campos em comum da entidade Feira."""
    nome: str

class FeiraCreate(FeiraBase):
    """Schema usado para validar os dados ao criar uma nova feira."""
    pass

class Feira(FeiraBase):
    """Schema usado para retornar os dados de uma feira via API."""
    feira_id: int
    model_config = ConfigDict(from_attributes=True)
