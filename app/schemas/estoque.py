from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime

class EstoqueBase(BaseModel):
    produto_id: int
    quantidade: int
    lote: Optional[str] = None
    data_producao: Optional[date] = None
    data_validade: Optional[date] = None
    localizacao: Optional[str] = None

class EstoqueCreate(EstoqueBase):
    pass

class Estoque(EstoqueBase):
    estoque_id: int
    data_atualizacao: datetime

    class Config:
        orm_mode = True
