from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app import crud, schemas
from app.database import get_db


router = APIRouter()

@router.get("/", response_model=list[schemas.Cliente])
def get_clientes(db: Session = Depends(get_db), skip: int = 0, limit: int = 100):
    return crud.get_clientes(db=db, skip=skip, limit=limit)

@router.get("/{cliente_id}", response_model=schemas.Cliente)
def get_cliente(cliente_id: int, db: Session = Depends(get_db)):
    return crud.get_cliente(db=db, cliente_id=cliente_id)

@router.post("/", response_model=schemas.Cliente)
def create_cliente(cliente: schemas.ClienteCreate, db: Session = Depends(get_db)):
    return crud.create_cliente(db=db, cliente=cliente)

@router.put("/{cliente_id}", response_model=schemas.Cliente)
def update_cliente(cliente_id: int, cliente: schemas.ClienteCreate, db: Session = Depends(get_db)):
    return crud.update_cliente(db=db, cliente_id=cliente_id, cliente=cliente)

@router.delete("/{cliente_id}", response_model=schemas.Cliente)
def delete_cliente(cliente_id: int, db: Session = Depends(get_db)):
    return crud.delete_cliente(db=db, cliente_id=cliente_id)
