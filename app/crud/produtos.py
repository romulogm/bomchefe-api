from sqlalchemy.orm import Session
from typing import Optional, List
from app.models import Produto, Estoque
from app.schemas import ProdutoCreate

def get_produtos(db: Session, skip: int = 0, limit: int = 100, feira_id: Optional[int] = None) -> List[Produto]:
    """
    Busca produtos no banco de dados.

    - Se um `feira_id` é fornecido, retorna apenas os produtos que têm estoque
      naquela feira e cuja quantidade seja maior que zero.
    - Se `feira_id` for None, retorna todos os produtos.
    """

    query = db.query(Produto)

    if feira_id is not None:
        query = query.join(Estoque).filter(
            Estoque.feira_id == feira_id,
            Estoque.quantidade > 0
        ).distinct()

    return query.offset(skip).limit(limit).all()


def get_produto(db: Session, produto_id: int):
    return db.query(Produto).filter(Produto.produto_id == produto_id).first()

def create_produto(db: Session, produto: ProdutoCreate):
    db_produto = Produto(**produto.dict())
    db.add(db_produto)
    db.commit()
    db.refresh(db_produto)
    return db_produto

def update_produto(db: Session, produto_id: int, produto: ProdutoCreate):
    db_produto = db.query(Produto).filter(Produto.produto_id == produto_id).first()
    if db_produto:
        for key, value in produto.dict().items():
            setattr(db_produto, key, value)
        db.commit()
        db.refresh(db_produto)
    return db_produto

def delete_produto(db: Session, produto_id: int):
    db_produto = db.query(Produto).filter(Produto.produto_id == produto_id).first()
    if db_produto:
        db.delete(db_produto)
        db.commit()
    return db_produto
