from sqlalchemy.orm import Session
from app.models import Cliente
from app.schemas import ClienteCreate

def get_clientes(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Cliente).offset(skip).limit(limit).all()

def get_cliente(db: Session, cliente_id: int):
    return db.query(Cliente).filter(Cliente.cliente_id == cliente_id).first()

def create_cliente(db: Session, cliente: ClienteCreate):
    db_cliente = Cliente(**cliente.dict())
    db.add(db_cliente)
    db.commit()
    db.refresh(db_cliente)
    return db_cliente

def update_cliente(db: Session, cliente_id: int, cliente: ClienteCreate):
    db_cliente = db.query(Cliente).filter(Cliente.cliente_id == cliente_id).first()
    if db_cliente:
        for key, value in cliente.dict().items():
            setattr(db_cliente, key, value)
        db.commit()
        db.refresh(db_cliente)
    return db_cliente

def delete_cliente(db: Session, cliente_id: int):
    db_cliente = db.query(Cliente).filter(Cliente.cliente_id == cliente_id).first()
    if db_cliente:
        db.delete(db_cliente)
        db.commit()
    return db_cliente
