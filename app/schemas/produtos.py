from pydantic import BaseModel
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

    class Config:
        orm_mode = True
