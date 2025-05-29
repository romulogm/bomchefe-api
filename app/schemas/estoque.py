from pydantic import BaseModel, ConfigDict
from datetime import date, datetime
from typing import Optional
from .produtos import Produto

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
    produto: Optional[Produto] = None 
    model_config = ConfigDict(from_attributes=True)
