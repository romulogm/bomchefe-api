from pydantic import BaseModel, ConfigDict
from decimal import Decimal
from datetime import date

class ProdutoBase(BaseModel):
    nome: str
    descricao: str = None
    categoria: str = None
    preco_unitario: Decimal
    peso_gramas: int = None
    data_criacao: date
    status: bool

class ProdutoCreate(ProdutoBase):
    pass

class Produto(ProdutoBase):
    produto_id: int

    ConfigDict(from_attributes=True)

class ProdutoSchema(BaseModel):
    """
    Schema para representar a informação essencial de um produto na resposta da API.
    """
    produto_id: int
    nome: str

    model_config = ConfigDict(from_attributes=True)