from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.schemas import produtos as schemas_produtos
from app.crud import produtos as crud_produtos
from app.database import get_db

router = APIRouter(
    prefix="/produtos",
    tags=["Produtos"]
)

@router.post("/", response_model=schemas_produtos.ProdutoOut)
def criar_produto(produto: schemas_produtos.ProdutoCreate, db: Session = Depends(get_db)):
    return crud_produtos.criar_produto(db, produto)

@router.get("/", response_model=List[schemas_produtos.ProdutoOut])
def listar_produtos(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud_produtos.listar_produtos(db, skip=skip, limit=limit)

@router.get("/{produto_id}", response_model=schemas_produtos.ProdutoOut)
def obter_produto(produto_id: int, db: Session = Depends(get_db)):
    db_produto = crud_produtos.obter_produto(db, produto_id)
    if db_produto is None:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    return db_produto

@router.put("/{produto_id}", response_model=schemas_produtos.ProdutoOut)
def atualizar_produto(produto_id: int, produto: schemas_produtos.ProdutoUpdate, db: Session = Depends(get_db)):
    db_produto = crud_produtos.atualizar_produto(db, produto_id, produto)
    if db_produto is None:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    return db_produto

@router.delete("/{produto_id}", response_model=schemas_produtos.ProdutoOut)
def deletar_produto(produto_id: int, db: Session = Depends(get_db)):
    db_produto = crud_produtos.deletar_produto(db, produto_id)
    if db_produto is None:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    return db_produto
