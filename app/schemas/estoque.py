from pydantic import BaseModel, ConfigDict, Field
from datetime import date, datetime
from typing import Optional, List
from .produtos import Produto, ProdutoSchema
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
    feira: Optional[Feira]
    movimentacoes_estoque: Optional[List[MovimentacaoEstoque]] = None
    vendas_associadas_a_este_estoque: Optional[List['ItemVendaResponseSchema']] = None
    model_config = ConfigDict(from_attributes=True)

class MovimentarEstoqueParaFeiraPayload(BaseModel):
    produto_id: int
    quantidade_a_mover: int = Field(..., gt=0)
    feira_id_destino: int

    
class MovimentarEstoqueResponse(BaseModel):
    message: str
    estoque_sede_id_atualizado: int
    estoque_sede_nova_quantidade: int
    novo_estoque_feira_id_criado: int
    novo_estoque_feira_quantidade: int
    
    ConfigDict(from_attributes=True)

class EstoqueComProdutoSchema(BaseModel):
    """
    Schema para o Estoque que expõe o Produto aninhado.
    Usado na resposta detalhada do ItemVenda.
    """
    estoque_id: int
    produto: ProdutoSchema

    model_config = ConfigDict(from_attributes=True)


from .itens_venda import ItemVendaResponseSchema
Estoque.model_rebuild()