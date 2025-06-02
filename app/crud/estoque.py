from sqlalchemy.orm import Session, joinedload
from app.models import Estoque, MovimentacaoEstoque
from app.schemas import EstoqueCreate, MovimentacaoEstoqueCreate
from .movimentacao_estoque import create_movimentacao_estoque

# def get_estoques(db: Session, skip: int = 0, limit: int = 100):
#     return db.query(Estoque).offset(skip).limit(limit).all()
def get_estoque(db: Session, estoque_id: int):
    # Carrega o item de estoque E O PRODUTO relacionado
    return db.query(Estoque)\
             .options(joinedload(Estoque.produto))\
             .filter(Estoque.estoque_id == estoque_id)\
             .first()
# def get_estoque(db: Session, estoque_id: int):
#     return db.query(Estoque).filter(Estoque.estoque_id == estoque_id).first()
def get_estoques(db: Session, skip: int = 0, limit: int = 100):
    # Carrega a lista de itens de estoque E OS PRODUTOS relacionados
    return db.query(Estoque)\
             .options(joinedload(Estoque.produto))\
             .offset(skip)\
             .limit(limit)\
             .all()

# def create_estoque(db: Session, estoque: EstoqueCreate):
#     db_estoque = Estoque(**estoque.model_dump())
#     db.add(db_estoque)
#     db.commit()
#     db.refresh(db_estoque)
#     return db_estoque

# def create_estoque(db: Session, estoque: EstoqueCreate):
#     # Criar o estoque
#     db_estoque = Estoque(**estoque.model_dump())
#     db.add(db_estoque)
#     db.commit()
#     db.refresh(db_estoque)

#     # Registrar movimentação
#     movimentacao = MovimentacaoEstoque(
#         produto_id=db_estoque.produto_id,
#         estoque_id=db_estoque.estoque_id,
#         quantidade_alterada=db_estoque.quantidade,
#         tipo_movimentacao="Estoque Adicionado",
#         feira_id=db_estoque.feira_id,
#         observacao="Registro inicial de estoque",
#     )
#     db.add(movimentacao)
#     db.commit()

#     return db_estoque

def create_estoque(db: Session, estoque: EstoqueCreate) -> EstoqueCreate: # estoque aqui é schemas.EstoqueCreate
    """Cria um novo item de estoque e uma movimentação inicial."""
    # Criar o estoque
    # Assume-se que EstoqueCreate não tem campos extras que EstoqueModel não aceita.
    # Se EstoqueCreate tiver campos como 'data_atualizacao' com default_factory,
    # model_dump() incluirá esse valor.
    db_estoque = Estoque(**estoque.model_dump())
    db.add(db_estoque)
    db.commit() # Primeiro commit para o estoque
    db.refresh(db_estoque) # Para obter estoque_id e outros defaults do BD

    # Registrar movimentação
    # Instancia diretamente o modelo MovimentacaoEstoqueModel
    # data_movimentacao usará o default do modelo SQLAlchemy se não for fornecido aqui.
    movimentacao = MovimentacaoEstoque(
        produto_id=db_estoque.produto_id,
        estoque_id=db_estoque.estoque_id,
        quantidade_alterada=db_estoque.quantidade, # Quantidade inicial é a quantidade alterada
        tipo_movimentacao="Estoque Adicionado", # Ou "entrada_inicial"
        feira_id=db_estoque.feira_id, # Presume que feira_id está em db_estoque
        observacao="Registro inicial de estoque",
        # venda_id e item_venda_id seriam None aqui
        # data_movimentacao será preenchida pelo default do modelo SQLAlchemy
    )
    db.add(movimentacao)
    db.commit() # Segundo commit para a movimentação

    return db_estoque

def update_estoque(db: Session, estoque_id: int, estoque: EstoqueCreate) -> Estoque | None:
    """
    Atualiza um item de estoque e registra uma movimentação para qualquer atualização via PUT.
    """
    db_estoque = get_estoque(db, estoque_id=estoque_id)
    if not db_estoque:
        return None

    quantidade_anterior = db_estoque.quantidade

    update_data = estoque.model_dump() 
    for key, value in update_data.items():
        setattr(db_estoque, key, value)
    
    quantidade_nova = db_estoque.quantidade
    quantidade_diferenca = quantidade_nova - quantidade_anterior
    
    tipo_movimentacao_log = "atualizacao_dados" 
    if quantidade_diferenca > 0:
        tipo_movimentacao_log = "ajuste_entrada_manual"
    elif quantidade_diferenca < 0:
        tipo_movimentacao_log = "ajuste_saida_manual"
    
    movimentacao_schema = MovimentacaoEstoqueCreate(
        produto_id=db_estoque.produto_id,
        estoque_id=estoque_id,
        quantidade_alterada=quantidade_diferenca,
        tipo_movimentacao=tipo_movimentacao_log,
        feira_id=db_estoque.feira_id, 
        observacao=f"Atualização do item de estoque ID {estoque_id} via endpoint PUT.",
    )
    create_movimentacao_estoque(db=db, movimentacao=movimentacao_schema) # create_movimentacao_estoque não faz commit
    
    db.commit() # Commit único para as alterações no estoque e a nova movimentação
    db.refresh(db_estoque)
    return db_estoque
# def update_estoque(db: Session, estoque_id: int, estoque: EstoqueCreate):
#     db_estoque = db.query(Estoque).filter(Estoque.estoque_id == estoque_id).first()
#     if db_estoque:
#         quantidade_anterior = db_estoque.quantidade

#         for key, value in estoque.model_dump().items():
#             setattr(db_estoque, key, value)

#         db.commit()
#         db.refresh(db_estoque)

#         # Registrar movimentação
#         quantidade_diferenca = db_estoque.quantidade - quantidade_anterior
#         if quantidade_diferenca != 0:
#             movimentacao = MovimentacaoEstoque(
#                 produto_id=db_estoque.produto_id,
#                 estoque_id=db_estoque.estoque_id,
#                 quantidade_alterada=quantidade_diferenca,
#                 tipo_movimentacao="Atualização de Estoque",
#                 feira_id=db_estoque.feira_id if hasattr(db_estoque, "feira_id") else None,
#                 observacao="Quantidade alterada via atualização de estoque",
#             )
#             db.add(movimentacao)
#             db.commit()

#     return db_estoque

def delete_estoque(db: Session, estoque_id: int):
    db_estoque = db.query(Estoque).filter(Estoque.estoque_id == estoque_id).first()
    if db_estoque:
        # Registrar movimentação antes de deletar
        movimentacao = MovimentacaoEstoque(
            produto_id=db_estoque.produto_id,
            estoque_id=db_estoque.estoque_id,
            quantidade_alterada=-db_estoque.quantidade,
            tipo_movimentacao="Remoção de Estoque",
            feira_id=db_estoque.feira_id if hasattr(db_estoque, "feira_id") else None,
            observacao="Estoque removido do sistema",
        )
        db.add(movimentacao)
        db.commit()

        # Deletar o estoque
        db.delete(db_estoque)
        db.commit()

    return db_estoque

# def update_estoque(db: Session, estoque_id: int, estoque: EstoqueCreate):
#     db_estoque = db.query(Estoque).filter(Estoque.estoque_id == estoque_id).first()
#     if db_estoque:
#         for key, value in estoque.dict().items():
#             setattr(db_estoque, key, value)
#         db.commit()
#         db.refresh(db_estoque)
#     return db_estoque

# def delete_estoque(db: Session, estoque_id: int):
#     db_estoque = db.query(Estoque).filter(Estoque.estoque_id == estoque_id).first()
#     if db_estoque:
#         db.delete(db_estoque)
#         db.commit()
#     return db_estoque
