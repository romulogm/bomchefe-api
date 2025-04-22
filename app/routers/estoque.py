from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import crud, schemas, models
from app.database import get_db

router = APIRouter()

@router.get("/", response_model=list[schemas.Estoque])
def get_estoques(db: Session = Depends(get_db), skip: int = 0, limit: int = 100):
    return crud.get_estoques(db=db, skip=skip, limit=limit)

@router.get("/{estoque_id}", response_model=schemas.Estoque)
def get_estoque(estoque_id: int, db: Session = Depends(get_db)):
    return crud.get_estoque(db=db, estoque_id=estoque_id)

@router.post("/", response_model=schemas.Estoque)
def create_estoque(estoque: schemas.EstoqueCreate, db: Session = Depends(get_db)):
    return crud.create_estoque(db=db, estoque=estoque)

@router.put("/{estoque_id}", response_model=schemas.Estoque)
def update_estoque(estoque_id: int, estoque: schemas.EstoqueCreate, db: Session = Depends(get_db)):
    return crud.update_estoque(db=db, estoque_id=estoque_id, estoque=estoque)

@router.delete("/{estoque_id}", response_model=schemas.Estoque)
def delete_estoque(estoque_id: int, db: Session = Depends(get_db)):
    return crud.delete_estoque(db=db, estoque_id=estoque_id)

@router.get("/produto/{produto_id}", response_model=list[schemas.estoque.Estoque])
def list_estoque_by_produto(produto_id: int, db: Session = Depends(get_db)):
    estoque = db.query(models.Estoque).filter(models.Estoque.produto_id == produto_id).all()

    if not estoque:
        raise HTTPException(status_code=404, detail="Nenhum estoque encontrado para este produto.")

    return estoque