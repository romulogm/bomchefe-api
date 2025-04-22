from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app import crud, schemas
from app.database import get_db

router = APIRouter()

@router.get("/", response_model=list[schemas.Produto])
def get_produtos(db: Session = Depends(get_db), skip: int = 0, limit: int = 100):
    return crud.get_produtos(db=db, skip=skip, limit=limit)

@router.get("/{produto_id}", response_model=schemas.Produto)
def get_produto(produto_id: int, db: Session = Depends(get_db)):
    return crud.get_produto(db=db, produto_id=produto_id)

@router.post("/", response_model=schemas.Produto)
def create_produto(produto: schemas.ProdutoCreate, db: Session = Depends(get_db)):
    return crud.create_produto(db=db, produto=produto)

@router.put("/{produto_id}", response_model=schemas.Produto)
def update_produto(produto_id: int, produto: schemas.ProdutoCreate, db: Session = Depends(get_db)):
    return crud.update_produto(db=db, produto_id=produto_id, produto=produto)

@router.delete("/{produto_id}", response_model=schemas.Produto)
def delete_produto(produto_id: int, db: Session = Depends(get_db)):
    return crud.delete_produto(db=db, produto_id=produto_id)
