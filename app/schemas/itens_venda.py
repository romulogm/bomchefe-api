from pydantic import BaseModel
from decimal import Decimal

class ItemVendaCreate(BaseModel):
    produto_id: int
    quantidade: int
    preco_unitario: Decimal

class ItemVendaUpdate(BaseModel):
    quantidade: int
    preco_unitario: Decimal
