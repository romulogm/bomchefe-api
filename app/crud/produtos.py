from sqlalchemy.orm import Session
from app.models import Produto
from app.schemas import ProdutoCreate

def get_produtos(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Produto).offset(skip).limit(limit).all()

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
