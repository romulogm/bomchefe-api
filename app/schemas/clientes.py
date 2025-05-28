from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional

class ClienteBase(BaseModel):
    tipo_pessoa: str
    documento: str
    nome: str
    email: Optional[EmailStr] = None
    endereco: Optional[str] = None

class ClienteCreate(ClienteBase):
    pass

class Cliente(ClienteBase):
    cliente_id: int

    model_config = ConfigDict(from_attributes=True)
