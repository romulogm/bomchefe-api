from sqlalchemy.orm import Session
from app import models
from app.schemas import clientes as schemas_clientes

def create_cliente(db: Session, cliente: schemas_clientes.ClienteCreate):
    db_cliente = models.clientes.Cliente(**cliente.dict())
    db.add(db_cliente)
    db.commit()
    db.refresh(db_cliente)
    return db_cliente

def get_cliente(db: Session, cliente_id: int):
    return db.query(models.clientes.Cliente).filter(models.clientes.Cliente.cliente_id == cliente_id).first()

def get_clientes(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.clientes.Cliente).offset(skip).limit(limit).all()

def update_cliente(db: Session, cliente_id: int, cliente_update: schemas_clientes.ClienteUpdate):
    db_cliente = db.query(models.clientes.Cliente).filter(models.clientes.Cliente.cliente_id == cliente_id).first()
    if db_cliente:
        for key, value in cliente_update.dict(exclude_unset=True).items():
            setattr(db_cliente, key, value)
        db.commit()
        db.refresh(db_cliente)
    return db_cliente

def delete_cliente(db: Session, cliente_id: int):
    db_cliente = db.query(models.clientes.Cliente).filter(models.clientes.Cliente.cliente_id == cliente_id).first()
    if db_cliente:
        db.delete(db_cliente)
        db.commit()
    return db_cliente
