from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app import crud, schemas
from app.database import get_db
from app.utils.auth import verify_token
from typing import List, Optional

router = APIRouter(dependencies=[Depends(verify_token)])

@router.get("/", response_model=List[schemas.Produto])
def listar_produtos(
    skip: int = 0,
    limit: int = 100,
    feira_id: Optional[int] = None, 
    db: Session = Depends(get_db)
):
    """
    Lista produtos. Filtra por feira se `feira_id` for fornecido.
    - Ex: /produtos
    - Ex: /produtos?feira_id=3
    """
    # A variável feira_id é passada para a função CRUD
    produtos = crud.produtos.get_produtos(db=db, skip=skip, limit=limit, feira_id=feira_id)
    return produtos

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
