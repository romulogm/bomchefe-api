from pydantic import BaseModel, ConfigDict, Field
from datetime import date, datetime
from typing import Optional, List
from .produtos import Produto
from .movimentacao_estoque import MovimentacaoEstoque
from .feiras import Feira


class EstoqueBase(BaseModel):
    produto_id: int
    feira_id: Optional[int] = None
    quantidade: int
    lote: Optional[str] = None
    data_producao: Optional[date] = None
    data_validade: Optional[date] = None
    localizacao: Optional[str] = None
    data_atualizacao: Optional[datetime] = Field(default_factory=datetime.utcnow)

class EstoqueCreate(EstoqueBase):
    pass

class Estoque(EstoqueBase):
    estoque_id: int
    produto: Optional[Produto] = None
    # feira_onde_alocado: Optional[Feira]
    movimentacoes_estoque: Optional[List[MovimentacaoEstoque]] = None
    model_config = ConfigDict(from_attributes=True)
