from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional

class EstoqueBase(BaseModel):
    produto_id: int
    quantidade: int
    lote: Optional[str] = None
    data_producao: Optional[date] = None
    data_validade: Optional[date] = None
    localizacao: Optional[str] = None
    data_atualizacao: datetime

class EstoqueCreate(EstoqueBase):
    pass

class Estoque(EstoqueBase):
    estoque_id: int

    class Config:
        orm_mode = True
