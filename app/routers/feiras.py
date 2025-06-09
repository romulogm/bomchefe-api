from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.utils.auth import verify_token
from .. import crud, schemas, models
from ..database import get_db

router = APIRouter(dependencies=[Depends(verify_token)])

@router.post("/", response_model=schemas.Feira, status_code=status.HTTP_201_CREATED)
def create_feira(feira_payload: schemas.FeiraCreate, db: Session = Depends(get_db)):
    """
    Cria uma nova feira.
    Impede a criação se já existir uma feira com o mesmo nome E mesma data.
    """
    db_feira_existente = crud.get_feira_by_name_and_date(
        db, nome=feira_payload.nome, data_feira=feira_payload.data
    )
    
    if db_feira_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Já existe uma feira com o nome '{feira_payload.nome}' na data '{feira_payload.data.strftime('%Y-%m-%d')}'."
        )

    # Criação da feira
    nova_feira = models.Feira(**feira_payload.dict())
    db.add(nova_feira)
    db.commit()
    db.refresh(nova_feira)

    return nova_feira


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