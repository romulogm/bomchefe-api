from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app import schemas, crud
from app.schemas import estoque
from app.database import get_db

router = APIRouter(
    prefix="/estoque",
    tags=["Estoque"]
)

@router.post("/", response_model=schemas.estoque.Estoque)
def create_estoque(estoque: schemas.estoque.EstoqueCreate, db: Session = Depends(get_db)):
    return crud.crud_estoque.create_estoque(db, estoque)

@router.get("/", response_model=List[schemas.estoque.Estoque])
def read_estoques(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.crud_estoque.get_estoques(db, skip=skip, limit=limit)

@router.get("/{estoque_id}", response_model=schemas.estoque.Estoque)
def read_estoque(estoque_id: int, db: Session = Depends(get_db)):
    db_estoque = crud.crud_estoque.get_estoque(db, estoque_id)
    if db_estoque is None:
        raise HTTPException(status_code=404, detail="Estoque não encontrado")
    return db_estoque

@router.put("/{estoque_id}", response_model=schemas.estoque.Estoque)
def update_estoque(estoque_id: int, estoque: schemas.estoque.EstoqueCreate, db: Session = Depends(get_db)):
    db_estoque = crud.crud_estoque.update_estoque(db, estoque_id, estoque)
    if db_estoque is None:
        raise HTTPException(status_code=404, detail="Estoque não encontrado")
    return db_estoque

@router.delete("/{estoque_id}")
def delete_estoque(estoque_id: int, db: Session = Depends(get_db)):
    db_estoque = crud.crud_estoque.delete_estoque(db, estoque_id)
    if db_estoque is None:
        raise HTTPException(status_code=404, detail="Estoque não encontrado")
    return {"message": "Estoque removido com sucesso"}
