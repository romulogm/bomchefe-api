from pydantic import BaseModel, ConfigDict, Field
from decimal import Decimal
from datetime import datetime 
from typing import Optional
from .produtos import Produto


class MovimentacaoEstoqueBase(BaseModel):
    produto_id: int
    estoque_id: int
    quantidade_alterada: int
    tipo_movimentacao: str
    feira_id: Optional[int] = None
    venda_id: Optional[int] = None
    item_venda_id: Optional[int] = None
    observacao: Optional[str] = None
    data_movimentacao: Optional[datetime] = Field(default_factory=datetime.utcnow)

class MovimentacaoEstoqueCreate(MovimentacaoEstoqueBase):
    pass

class MovimentacaoEstoque(MovimentacaoEstoqueBase):
    movimentacao_id: int
    produto: Optional[Produto] = None
    data_movimentacao: datetime 

    # estoque_afetado: Optional[Estoque] = None # Cuidado com circularidade se Estoque também tiver lista de Movimentacoes
    # feira: Optional[Feira] = None
    # venda_associada: Optional[Venda] = None # Cuidado com circularidade
    model_config = ConfigDict(from_attributes=True)
