from pydantic import BaseModel, EmailStr
from typing import Optional

class ClienteBase(BaseModel):
    tipo_pessoa: str
    documento: str
    nome: str
    email: Optional[EmailStr] = None
    endereco: Optional[str] = None

class ClienteCreate(ClienteBase):
    pass

class ClienteUpdate(ClienteBase):
    pass

class ClienteOut(ClienteBase):
    cliente_id: int

    class Config:
        orm_mode = True
