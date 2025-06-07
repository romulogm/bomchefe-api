from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from .feiras import Feira
from.itens_venda import ItemVendaBase, ItemVendaCreate


class VendaBase(BaseModel):

    cliente_id: Optional[int] = None
    valor_total: Decimal 
    status_venda: str = "Concluída" 
    feira_id: Optional[int] = None

class VendaCreate(VendaBase):
    itens_venda: List[ItemVendaCreate] = Field(default_factory=list)


class Venda(VendaBase):

    venda_id: int
    data_venda: datetime
    itens_venda: List[ItemVendaBase] = Field(default_factory=list) 
    feira: Optional[Feira] = None

    model_config = ConfigDict(from_attributes=True)

class VendaUpdate(BaseModel):

    cliente_id: Optional[int] = None
    valor_total: Optional[Decimal] = None 
    status_venda: Optional[str] = None
    feira_id: Optional[int] = None
    itens_venda: Optional[List[ItemVendaBase]] = None

    model_config = ConfigDict(from_attributes=True)

class ConsolidarVendaPayload(BaseModel):
    """Payload para solicitar a consolidação de uma feira a partir de uma venda."""
    venda_id: int = Field(..., description="ID da venda que aciona a consolidação da feira associada.")

class ProdutoVendido(BaseModel):
    """Descreve um produto que foi vendido na feira."""
    produto_id: int
    nome_produto: str
    quantidade_total_vendida: int
    valor_total_arrecadado: float

class ProdutoRetornado(BaseModel):
    """Descreve um produto cujo estoque foi retornado da feira para a sede."""
    produto_id: int
    nome_produto: str
    quantidade_retornada: float
    estoque_feira_id_zerado: int
    estoque_sede_id_atualizado: int
    nova_quantidade_sede: float

class ConsolidarVendaResponse(BaseModel):
    """Resposta detalhada da operação de consolidação da feira."""
    message: str
    feira_id: int
    produtos_vendidos: List[ProdutoVendido]
    produtos_retornados: List[ProdutoRetornado]
