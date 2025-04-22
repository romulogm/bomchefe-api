from pydantic import BaseModel
from datetime import datetime
from decimal import Decimal
from typing import List, Optional

class ItemVendaBase(BaseModel):
    produto_id: int
    quantidade: int
    preco_unitario: Decimal
    subtotal: Decimal

class VendaBase(BaseModel):
    cliente_id: int
    valor_total: Decimal
    metodo_pagamento: Optional[str] = None
    status_venda: str = "Pendente"

class VendaCreate(VendaBase):
    pass

class Venda(VendaBase):
    venda_id: int
    data_venda: datetime
    itens_venda: List[ItemVendaBase] = []

    class Config:
        orm_mode = True
