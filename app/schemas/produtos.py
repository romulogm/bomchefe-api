from pydantic import BaseModel
from typing import Optional
from datetime import date

class ProdutoBase(BaseModel):
    nome: str
    descricao: Optional[str] = None
    categoria: Optional[str] = None
    preco_unitario: float
    peso_gramas: Optional[int] = None
    status: Optional[bool] = True

class ProdutoCreate(ProdutoBase):
    pass

class ProdutoUpdate(ProdutoBase):
    pass

class ProdutoOut(ProdutoBase):
    produto_id: int
    data_criacao: date

    class Config:
        orm_mode = True
