from pydantic import BaseModel, ConfigDict
from decimal import Decimal
from typing import Optional

class ItemVendaBase(BaseModel):
    quantidade: int
    preco_unitario: Decimal

class ItemVendaCreate(ItemVendaBase):
    estoque_id: int 
    model_config = ConfigDict(from_attributes=True)

class ItemVendaUpdate(BaseModel):
    quantidade_vendida: Optional[int] = None
    preco_unitario: Optional[Decimal] = None

    model_config = ConfigDict(from_attributes=True)

class ItemVendaResponseSchema(BaseModel):
    # Campos que estavam faltando na resposta
    item_venda_id: int
    venda_id: int
    estoque_id: int
    
    # Campos que já estavam na resposta
    quantidade: int
    preco_unitario: Decimal

    # Garante que o Pydantic consiga ler os dados do modelo SQLAlchemy
    model_config = ConfigDict(from_attributes=True)
    # item_venda_id: int
    # venda_id: int
    # estoque_id: int 

    # model_config = ConfigDict(from_attributes=True)

    
