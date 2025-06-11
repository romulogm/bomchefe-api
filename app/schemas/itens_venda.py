from pydantic import BaseModel, ConfigDict
from decimal import Decimal
from typing import Optional
from .estoque import EstoqueComProdutoSchema

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
  
    item_venda_id: int
    venda_id: int
    estoque_id: int
    
    quantidade: int
    preco_unitario: Decimal

    model_config = ConfigDict(from_attributes=True)
 

    

class ItemVendaDetalhadoSchema(BaseModel):
    """
    Schema de resposta para um item de venda que inclui detalhes
    do produto através do relacionamento com o estoque.
    """
    item_venda_id: int
    quantidade: int
    preco_unitario: Decimal
    
    item_de_estoque_utilizado: EstoqueComProdutoSchema

    model_config = ConfigDict(from_attributes=True)