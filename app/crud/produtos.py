from sqlalchemy.orm import Session
from app.models.produtos import Produto
from app.schemas.produtos import ProdutoCreate, ProdutoUpdate

def criar_produto(db: Session, produto: ProdutoCreate):
    db_produto = Produto(**produto.dict())
    db.add(db_produto)
    db.commit()
    db.refresh(db_produto)
    return db_produto

def listar_produtos(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Produto).offset(skip).limit(limit).all()

def obter_produto(db: Session, produto_id: int):
    return db.query(Produto).filter(Produto.produto_id == produto_id).first()

def atualizar_produto(db: Session, produto_id: int, produto: ProdutoUpdate):
    db_produto = db.query(Produto).filter(Produto.produto_id == produto_id).first()
    if db_produto is None:
        return None

    for key, value in produto.dict(exclude_unset=True).items():
        setattr(db_produto, key, value)

    db.commit()
    db.refresh(db_produto)
    return db_produto

def deletar_produto(db: Session, produto_id: int):
    db_produto = db.query(Produto).filter(Produto.produto_id == produto_id).first()
    if db_produto:
        db.delete(db_produto)
        db.commit()
    return db_produto
