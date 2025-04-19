from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.crud import clientes as crud_clientes
from app.schemas import clientes as schemas_clientes
from app.database import get_db

router = APIRouter(
    prefix="/clientes",
    tags=["clientes"],
)

@router.post("/", response_model=schemas_clientes.ClienteOut)
def criar_cliente(cliente: schemas_clientes.ClienteCreate, db: Session = Depends(get_db)):
    return crud_clientes.create_cliente(db, cliente)

@router.get("/{cliente_id}", response_model=schemas_clientes.ClienteOut)
def buscar_cliente(cliente_id: int, db: Session = Depends(get_db)):
    cliente = crud_clientes.get_cliente(db, cliente_id)
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    return cliente

@router.get("/", response_model=List[schemas_clientes.ClienteOut])
def listar_clientes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud_clientes.get_clientes(db, skip=skip, limit=limit)

@router.put("/{cliente_id}", response_model=schemas_clientes.ClienteOut)
def atualizar_cliente(cliente_id: int, cliente_update: schemas_clientes.ClienteUpdate, db: Session = Depends(get_db)):
    cliente = crud_clientes.update_cliente(db, cliente_id, cliente_update)
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    return cliente

@router.delete("/{cliente_id}")
def deletar_cliente(cliente_id: int, db: Session = Depends(get_db)):
    cliente = crud_clientes.delete_cliente(db, cliente_id)
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    return {"ok": True}
