from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from .. import crud, schemas
from ..database import get_db

router = APIRouter(
    prefix="/feiras",  
    tags=["Feiras"]    
)

@router.post("/", response_model=schemas.Feira, status_code=status.HTTP_201_CREATED)
def create_feira(feira: schemas.FeiraCreate, db: Session = Depends(get_db)):
    """
    Cria uma nova feira.
    Verifica se já não existe uma feira com o mesmo nome.
    """
    db_feira = crud.get_feira_by_name(db, nome=feira.nome)
    if db_feira:
        raise HTTPException(status_code=400, detail="Feira com este nome já existe.")
    return crud.create_feira(db=db, feira=feira)

@router.get("/", response_model=List[schemas.Feira])
def read_feiras(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Retorna uma lista de todas as feiras cadastradas.
    """
    feiras = crud.get_feiras(db, skip=skip, limit=limit)
    return feiras

@router.get("/{feira_id}", response_model=schemas.Feira)
def read_feira(feira_id: int, db: Session = Depends(get_db)):
    """
    Retorna os detalhes de uma feira específica pelo seu ID.
    """
    db_feira = crud.get_feira(db, feira_id=feira_id)
    if db_feira is None:
        raise HTTPException(status_code=404, detail="Feira não encontrada.")
    return db_feira

@router.put("/{feira_id}", response_model=schemas.Feira)
def update_feira(feira_id: int, feira: schemas.FeiraCreate, db: Session = Depends(get_db)):
    """
    Atualiza o nome de uma feira existente.
    """
    db_feira = crud.update_feira(db=db, feira_id=feira_id, feira=feira)
    if db_feira is None:
        raise HTTPException(status_code=404, detail="Feira não encontrada para atualização.")
    return db_feira

@router.delete("/{feira_id}", response_model=schemas.Feira)
def delete_feira(feira_id: int, db: Session = Depends(get_db)):
    """
    Deleta uma feira existente.
    """
    db_feira = crud.delete_feira(db=db, feira_id=feira_id)
    if db_feira is None:
        raise HTTPException(status_code=404, detail="Feira não encontrada para exclusão.")
    return db_feira