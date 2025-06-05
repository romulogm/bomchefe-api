from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
# Removido ForeignKeyViolation pois o handler genérico de IntegrityError é melhor
# from psycopg2.errors import ForeignKeyViolation # Específico do psycopg2
from app import crud, schemas, models
from app.database import get_db
from pydantic import BaseModel, Field # Adicionado para os novos schemas

router = APIRouter()

@router.get("/", response_model=list[schemas.Estoque]) # Usando MovimentarMovimentarEstoqueResponse do seu schema
def get_estoques_endpoint(db: Session = Depends(get_db), skip: int = 0, limit: int = 100):
    """
    Lista todos os itens de estoque com seus produtos relacionados.
    """
    return crud.estoque.get_estoques(db=db, skip=skip, limit=limit)

@router.get("/{estoque_id}", response_model=schemas.Estoque) # Usando MovimentarEstoqueResponse
def get_estoque_endpoint(estoque_id: int, db: Session = Depends(get_db)):
    """
    Obtém um item de estoque específico pelo seu ID.
    """
    db_estoque = crud.estoque.get_estoque(db=db, estoque_id=estoque_id)
    if db_estoque is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item de estoque não encontrado.")
    return db_estoque

@router.post("/", response_model=schemas.Estoque, status_code=status.HTTP_201_CREATED) # Usando MovimentarEstoqueResponse
def create_estoque_endpoint(estoque: schemas.EstoqueCreate, db: Session = Depends(get_db)):
    """
    Cria um novo item de estoque e a movimentação inicial correspondente.
    """
    try:
        return crud.estoque.create_estoque(db=db, estoque_data=estoque)
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erro de integridade ao criar estoque. Verifique se o produto_id e feira_id (se fornecido) existem. Detalhe: {str(e.orig)}"
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro inesperado ao criar estoque: {str(e)}"
        )


@router.put("/{estoque_id}", response_model=schemas.Estoque) # Usando MovimentarEstoqueResponse
def update_estoque_endpoint(estoque_id: int, estoque_update_data: schemas.EstoqueCreate, db: Session = Depends(get_db)):
    """
    Atualiza um item de estoque existente e registra as movimentações.
    """
    db_estoque_existente = crud.estoque.get_estoque(db, estoque_id=estoque_id)
    if db_estoque_existente is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item de estoque não encontrado para atualização.")
    
    try:
        updated_estoque = crud.estoque.update_estoque(db=db, estoque_id=estoque_id, estoque_data=estoque_update_data)
        return updated_estoque
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erro de integridade ao atualizar estoque. Verifique se o produto_id e feira_id (se fornecido) existem. Detalhe: {str(e.orig)}"
        )
    except HTTPException: 
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro inesperado ao atualizar estoque: {str(e)}"
        )

@router.delete("/{estoque_id}", response_model=schemas.Estoque) # Usando MovimentarEstoqueResponse
def delete_estoque_endpoint(estoque_id: int, db: Session = Depends(get_db)):
    """
    Deleta um item de estoque e registra a movimentação de remoção total.
    """
    db_estoque = crud.estoque.delete_estoque(db=db, estoque_id=estoque_id)
    if db_estoque is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item de estoque não encontrado para deletar.")
    return db_estoque

@router.get("/produto/{produto_id}", response_model=list[schemas.estoque.Estoque]) # Usando MovimentarEstoqueResponse
def list_estoque_by_produto_endpoint(produto_id: int, db: Session = Depends(get_db)):
    """
    Lista todos os estoques associados a um produto específico.
    """
    estoques = db.query(models.Estoque).filter(models.Estoque.produto_id == produto_id).all()
    if not estoques:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Nenhum estoque encontrado para este produto.")
    return estoques

# --- NOVO ENDPOINT ---
@router.post("/movimentar-para-feira/", response_model=schemas.MovimentarEstoqueResponse, status_code=status.HTTP_200_OK)
def movimentar_estoque_para_feira_endpoint(
    payload: schemas.MovimentarEstoqueParaFeiraPayload, 
    db: Session = Depends(get_db)
):
    """
    Move uma quantidade de um produto do estoque da "Sede" (localizacao="Sede", feira_id=None)
    para um novo registro de estoque em uma feira de destino.
    Registra as movimentações de saída da Sede e entrada na Feira.
    """
    try:
        # CORRIGIDO: Chamada para crud.estoque.movimentar_estoque_para_feira
        resultado_movimentacao = crud.estoque.movimentar_estoque_para_feira(db=db, payload=payload)
        return resultado_movimentacao
    except HTTPException as http_exc: 
        raise http_exc
    except IntegrityError as e: 
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erro de integridade durante a movimentação: {str(e.orig)}"
        )
    except Exception as e: 
        db.rollback()
        # Idealmente, logar o erro 'e' aqui para depuração no servidor
        # import logging
        # logger = logging.getLogger(__name__)
        # logger.error(f"Erro inesperado em movimentar_estoque_para_feira_endpoint: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ocorreu um erro interno inesperado ao processar a movimentação de estoque: {str(e)}"
        )