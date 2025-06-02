from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from psycopg2.errors import ForeignKeyViolation

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

# @router.put("/{estoque_id}", response_model=schemas.Estoque)
# def update_estoque_endpoint(estoque_id: int, estoque_update_payload: schemas.EstoqueCreate, db: Session = Depends(get_db)):
#     """
#     Atualiza um item de estoque existente.
#     Verifica se o feira_id (se fornecido) existe.
#     """
#     # Primeiro, verifica se o item de estoque existe
#     db_estoque_existente = crud.get_estoque(db, estoque_id=estoque_id) # Supondo que você tenha crud.get_estoque
#     if db_estoque_existente is None:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item de estoque não encontrado.")

#     try:
#         # print(f"Router: Payload recebido para atualizar estoque {estoque_id}: {estoque_update_payload.model_dump_json(indent=2)}") # Debug opcional
#         updated_estoque = crud.update_estoque(db=db, estoque_id=estoque_id, estoque_update_data=estoque_update_payload) # Ajuste o nome do parâmetro no CRUD se necessário
#         if updated_estoque is None: # Caso o CRUD retorne None por algum motivo (além de não encontrar)
#             raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item de estoque não encontrado para atualização.")
#         return updated_estoque
        
#     except IntegrityError as e:
#         db.rollback()
#         original_exception = getattr(e, 'orig', None)
        
#         if isinstance(original_exception, ForeignKeyViolation):
#             detail_message = "Um valor de chave estrangeira fornecido para atualização não existe na tabela referenciada."
#             constraint_name = str(getattr(original_exception.diag, 'constraint_name', '')) if hasattr(original_exception, 'diag') else ''

#             if estoque_update_payload.feira_id is not None and 'feira_id' in constraint_name:
#                  detail_message = f"O 'feira_id' ({estoque_update_payload.feira_id}) fornecido para atualização não existe na tabela de feiras. Se o item de estoque não deve ser associado a uma feira, omita o campo 'feira_id' ou envie 'feira_id: null'."
#             elif 'produto_id' in constraint_name:
#                  detail_message = f"O 'produto_id' ({estoque_update_payload.produto_id}) fornecido para atualização não existe na tabela de produtos."
            
#             raise HTTPException(
#                 status_code=status.HTTP_400_BAD_REQUEST,
#                 detail=detail_message
#             )
#         else:
#             # Outras IntegrityErrors
#             raise HTTPException(
#                 status_code=status.HTTP_400_BAD_REQUEST,
#                 detail="Ocorreu um erro ao atualizar devido a uma restrição de dados. Verifique os valores fornecidos."
#             )
#     except Exception as e:
#         db.rollback()
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail="Ocorreu um erro inesperado ao atualizar o item de estoque."
#         )

@router.delete("/{estoque_id}", response_model=schemas.Estoque)
def delete_estoque(estoque_id: int, db: Session = Depends(get_db)):
    return crud.delete_estoque(db=db, estoque_id=estoque_id)

@router.get("/produto/{produto_id}", response_model=list[schemas.estoque.Estoque])
def list_estoque_by_produto(produto_id: int, db: Session = Depends(get_db)):
    estoque = db.query(models.Estoque).filter(models.Estoque.produto_id == produto_id).all()

    if not estoque:
        raise HTTPException(status_code=404, detail="Nenhum estoque encontrado para este produto.")

    return estoque