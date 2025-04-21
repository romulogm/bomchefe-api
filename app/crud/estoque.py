from sqlalchemy.orm import Session
from app.models.estoque import Estoque
from app.schemas.estoque import EstoqueCreate

def create_estoque(db: Session, estoque: EstoqueCreate):
    db_estoque = Estoque(**estoque.dict())
    db.add(db_estoque)
    db.commit()
    db.refresh(db_estoque)
    return db_estoque

def get_estoques(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Estoque).offset(skip).limit(limit).all()

def get_estoque(db: Session, estoque_id: int):
    return db.query(Estoque).filter(Estoque.estoque_id == estoque_id).first()

def update_estoque(db: Session, estoque_id: int, estoque_data: EstoqueCreate):
    db_estoque = get_estoque(db, estoque_id)
    if db_estoque:
        for key, value in estoque_data.dict().items():
            setattr(db_estoque, key, value)
        db.commit()
        db.refresh(db_estoque)
    return db_estoque

def delete_estoque(db: Session, estoque_id: int):
    db_estoque = get_estoque(db, estoque_id)
    if db_estoque:
        db.delete(db_estoque)
        db.commit()
    return db_estoque
