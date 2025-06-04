from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from .feiras import Feira
from.itens_venda import ItemVendaBase, ItemVendaCreate

# class ItemVendaBase(BaseModel):

#     estoque_id: int
#     quantidade: int
#     preco_unitario: Decimal

#     model_config = ConfigDict(from_attributes=True)

# class ItemVendaCreate(BaseModel): 
#     estoque_id: int
#     quantidade: int
#     preco_unitario: Decimal

#     model_config = ConfigDict(from_attributes=True)


class VendaBase(BaseModel):

    cliente_id: Optional[int] = None
    valor_total: Decimal # Atenção: Este campo é tipicamente calculado.
    status_venda: str = "Concluída" # Default conforme sua definição
    feira_id: Optional[int] = None

class VendaCreate(VendaBase):

    # Se você usar ItemVendaCreate para os itens na criação:
    # itens_venda: List[ItemVendaCreate] = []
    # Conforme sua definição original, usando ItemVendaBase:
    itens_venda: List[ItemVendaCreate] = Field(default_factory=list)
    # 'valor_total' em VendaBase será o valor enviado pelo cliente.
    # A lógica de negócios deve validar ou recalcular isso com base nos itens.

class Venda(VendaBase): # Schema para respostas da API

    venda_id: int
    data_venda: datetime
    itens_venda: List[ItemVendaBase] = Field(default_factory=list) # Ou um schema ItemVendaResponse mais detalhado
    feira: Optional[Feira] = None

    model_config = ConfigDict(from_attributes=True)

class VendaUpdate(BaseModel):

    cliente_id: Optional[int] = None
    valor_total: Optional[Decimal] = None 
    status_venda: Optional[str] = None
    feira_id: Optional[int] = None
    
    itens_venda: Optional[List[ItemVendaBase]] = None

    model_config = ConfigDict(from_attributes=True)