from pydantic import BaseModel, ConfigDict
from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from .feiras import Feira

class ItemVendaBase(BaseModel):
    produto_id: int
    quantidade: int
    preco_unitario: Decimal
    subtotal: Decimal
    
    model_config = ConfigDict(from_attributes=True)

class VendaBase(BaseModel):
    cliente_id: int
    valor_total: Decimal
    metodo_pagamento: Optional[str] = None
    status_venda: str = "Pendente"
    feira_id: Optional[int] = None

class VendaCreate(VendaBase):
    pass

class Venda(VendaBase):
    venda_id: int
    data_venda: datetime
    itens_venda: List[ItemVendaBase] = []
    feira: Optional[Feira] = None   

    model_config = ConfigDict(from_attributes=True)
