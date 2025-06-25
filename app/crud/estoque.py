from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException, status
from datetime import datetime
from app import models, schemas

def get_estoque(db: Session, estoque_id: int):
    return db.query(models.Estoque)\
             .options(joinedload(models.Estoque.produto))\
             .filter(models.Estoque.estoque_id == estoque_id)\
             .first()

def get_estoques(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Estoque)\
             .options(joinedload(models.Estoque.produto))\
             .offset(skip)\
             .limit(limit)\
             .all()

def create_estoque(db: Session, estoque_data: schemas.EstoqueCreate) -> models.Estoque:
    """
    Cria um novo item de estoque.

    Antes de criar, verifica se já existe um estoque para o mesmo produto na "Sede".
    Se já existir, impede a criação de um novo para evitar duplicidade.
    """


    if estoque_data.localizacao == "Sede":
        estoque_existente_na_sede = db.query(models.Estoque).filter(
            models.Estoque.produto_id == estoque_data.produto_id,
            models.Estoque.localizacao == "Sede"
        ).first()

      
        if estoque_existente_na_sede:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, 
                detail=f"Já existe um estoque para o produto ID {estoque_data.produto_id} na Sede. Não é permitido criar um novo."
            )
   
    # --- INÍCIO DA ALTERAÇÃO ---

    dados_para_db = estoque_data.model_dump()
    if dados_para_db.get("feira_id") == 0:
        dados_para_db["feira_id"] = None

    db_estoque = models.Estoque(**dados_para_db)    

    # --- FIM DA ALTERAÇÃO ---  

    db.add(db_estoque)
    db.flush() 

    movimentacao = models.MovimentacaoEstoque(
        produto_id=db_estoque.produto_id,
        estoque_id=db_estoque.estoque_id,
        quantidade_alterada=db_estoque.quantidade,
        tipo_movimentacao="ENTRADA_INICIAL_ESTOQUE", 
        feira_id=db_estoque.feira_id,
        observacao="Registo inicial de estoque criado.",
    )
    db.add(movimentacao)
    
    try:
        db.commit()
        db.refresh(db_estoque)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao criar estoque e movimentação inicial: {str(e)}"
        )
    return db_estoque

def update_estoque(db: Session, estoque_id: int, estoque_data: schemas.EstoqueCreate) -> models.Estoque | None:
    db_estoque = db.query(models.Estoque).filter(models.Estoque.estoque_id == estoque_id).with_for_update().first()
    if not db_estoque:
        return None

    quantidade_anterior = db_estoque.quantidade
    produto_id_anterior = db_estoque.produto_id 

    update_fields = estoque_data.model_dump(exclude_unset=True)
    for key, value in update_fields.items():
        setattr(db_estoque, key, value)
    
    db_estoque.data_atualizacao = datetime.utcnow() 

    quantidade_nova = db_estoque.quantidade
    quantidade_diferenca = quantidade_nova - quantidade_anterior
    
    if quantidade_diferenca != 0 or db_estoque.produto_id != produto_id_anterior:
        tipo_movimentacao_log = "AJUSTE_DADOS_ESTOQUE" 
        if quantidade_diferenca > 0:
            tipo_movimentacao_log = "AJUSTE_ENTRADA_MANUAL"
        elif quantidade_diferenca < 0:
            tipo_movimentacao_log = "AJUSTE_SAIDA_MANUAL"
        
        observacao_mov = f"Atualização do item de estoque ID {estoque_id}."
        if db_estoque.produto_id != produto_id_anterior:
            observacao_mov += f" Produto alterado de ID {produto_id_anterior} para {db_estoque.produto_id}."
        if quantidade_diferenca != 0:
             observacao_mov += f" Quantidade alterada de {quantidade_anterior} para {quantidade_nova} (diferença: {quantidade_diferenca})."


        movimentacao = models.MovimentacaoEstoque(
            produto_id=db_estoque.produto_id, 
            estoque_id=estoque_id,
            quantidade_alterada=quantidade_diferenca,
            tipo_movimentacao=tipo_movimentacao_log,
            feira_id=db_estoque.feira_id, 
            observacao=observacao_mov,
        )
        db.add(movimentacao)
    
    try:
        db.commit()
        db.refresh(db_estoque)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao atualizar estoque: {str(e)}"
        )
    return db_estoque

def delete_estoque(db: Session, estoque_id: int) -> models.Estoque | None:
    db_estoque = db.query(models.Estoque).filter(models.Estoque.estoque_id == estoque_id).first()
    if db_estoque:
        movimentacao = models.MovimentacaoEstoque(
            produto_id=db_estoque.produto_id,
            estoque_id=db_estoque.estoque_id,
            quantidade_alterada=-db_estoque.quantidade, 
            tipo_movimentacao="REMOCAO_TOTAL_ESTOQUE",
            feira_id=db_estoque.feira_id,
            observacao=f"Remoção completa do registo de estoque ID {estoque_id}.",
        )
        db.add(movimentacao)
        
        db.delete(db_estoque)
        
        try:
            db.commit() 
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro ao eliminar estoque e registar movimentação: {str(e)}"
            )
        return db_estoque 
    return None

def movimentar_estoque_para_feira(
    db: Session, 
    payload: schemas.MovimentarEstoqueParaFeiraPayload # Usando o schema Pydantic para o payload
) -> dict: 
    """
    Move uma quantidade de um produto do estoque da "Sede" para um novo estoque numa feira.
    """
    produto_id = payload.produto_id
    quantidade_a_mover = payload.quantidade_a_mover
    feira_id_destino = payload.feira_id_destino

    # 1. Valida se a feira de destino existe
    feira_destino = db.query(models.Feira).filter(models.Feira.feira_id == feira_id_destino).first()
    if not feira_destino:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Feira de destino com ID {feira_id_destino} não encontrada."
        )

    # 2. Encontra o estoque da "Sede" para o produto_id especificado
    # "Sede" é identificada por feira_id=None E localizacao="Sede"
    estoque_sede = db.query(models.Estoque)\
                     .filter(
                         models.Estoque.produto_id == produto_id,
                         models.Estoque.feira_id.is_(None), # Garante que é da Sede (sem feira)
                         models.Estoque.localizacao == "Sede" # Conforme requisito
                     )\
                     .with_for_update()\
                     .first()

    if not estoque_sede:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"estoque da Sede para o produto ID {produto_id} com localização 'Sede' não encontrado."
        )

    # 3. Verifica se há quantidade suficiente na Sede
    if estoque_sede.quantidade < quantidade_a_mover:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"estoque insuficiente na Sede para o produto ID {produto_id}. "
                   f"Disponível: {estoque_sede.quantidade}, Solicitado: {quantidade_a_mover}."
        )

    # 4. Subtrai a quantidade do estoque da Sede
    estoque_sede.quantidade -= quantidade_a_mover
    estoque_sede.data_atualizacao = datetime.utcnow()

    # 5. Cria o novo registo de estoque para a Feira
    # Apenas os campos essenciais são definidos; outros serão NULL ou defaults do modelo.
    # A 'localizacao' do novo estoque da feira pode ser definida como 'Feira [Nome da Feira]' ou similar.
    db_novo_estoque_feira = models.Estoque(
        produto_id=produto_id,
        quantidade=quantidade_a_mover,
        feira_id=feira_id_destino,
        localizacao=f"Feira {feira_destino.nome}", # Define uma localização para o estoque da feira
        data_atualizacao=datetime.utcnow()
        # Os campos lote, data_producao, data_validade serão NULL
        # a menos que o modelo Estoque tenha defaults ou você decida passá-los de alguma forma.
    )
    db.add(db_novo_estoque_feira)
    db.flush() # Para obter o db_novo_estoque_feira.estoque_id

    # 6. Cria MovimentacaoEstoque de SAÍDA da Sede
    mov_saida_sede = models.MovimentacaoEstoque(
        produto_id=produto_id,
        estoque_id=estoque_sede.estoque_id,
        quantidade_alterada=-quantidade_a_mover,
        tipo_movimentacao='SAIDA_SEDE_PARA_FEIRA',
        feira_id=feira_id_destino, 
        observacao=f"Saída de {quantidade_a_mover} unidades do produto ID {produto_id} da Sede para Feira ID {feira_id_destino} ({feira_destino.nome})."
    )
    db.add(mov_saida_sede)

    # 7. Cria MovimentacaoEstoque de ENTRADA na Feira
    mov_entrada_feira = models.MovimentacaoEstoque(
        produto_id=produto_id,
        estoque_id=db_novo_estoque_feira.estoque_id, 
        quantidade_alterada=quantidade_a_mover,
        tipo_movimentacao='ENTRADA_FEIRA_DA_SEDE',
        feira_id=feira_id_destino,
        observacao=f"Entrada de {quantidade_a_mover} unidades do produto ID {produto_id} na Feira ID {feira_id_destino} ({feira_destino.nome}), proveniente da Sede."
    )
    db.add(mov_entrada_feira)

    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ocorreu um erro ao tentar movimentar o estoque para a feira: {str(e)}"
        )
    
    db.refresh(estoque_sede)
    db.refresh(db_novo_estoque_feira)
    
    return {
        "message": "Movimentação de estoque para feira realizada com sucesso.",
        "estoque_sede_id_atualizado": estoque_sede.estoque_id,
        "estoque_sede_nova_quantidade": estoque_sede.quantidade,
        "novo_estoque_feira_id_criado": db_novo_estoque_feira.estoque_id,
        "novo_estoque_feira_quantidade": db_novo_estoque_feira.quantidade
    }


# from sqlalchemy.orm import Session, joinedload
# from app.models import Estoque, MovimentacaoEstoque
# from app.schemas import EstoqueCreate, MovimentacaoEstoqueCreate
# from .movimentacao_estoque import create_movimentacao_estoque


# def get_estoque(db: Session, estoque_id: int):

#     return db.query(Estoque)\
#              .options(joinedload(Estoque.produto))\
#              .filter(Estoque.estoque_id == estoque_id)\
#              .first()

# def get_estoques(db: Session, skip: int = 0, limit: int = 100):
#     # Carrega a lista de itens de estoque E OS PRODUTOS relacionados
#     return db.query(Estoque)\
#              .options(joinedload(Estoque.produto))\
#              .offset(skip)\
#              .limit(limit)\
#              .all()

# def create_estoque(db: Session, estoque: EstoqueCreate) -> EstoqueCreate: # estoque aqui é schemas.EstoqueCreate
#     """Cria um novo item de estoque e uma movimentação inicial."""
    
#     db_estoque = Estoque(**estoque.model_dump())
#     db.add(db_estoque)
#     db.commit() # Primeiro commit para o estoque
#     db.refresh(db_estoque) # Para obter estoque_id e outros defaults do BD

#     movimentacao = MovimentacaoEstoque(
#         produto_id=db_estoque.produto_id,
#         estoque_id=db_estoque.estoque_id,
#         quantidade_alterada=db_estoque.quantidade, # Quantidade inicial é a quantidade alterada
#         tipo_movimentacao="Estoque Adicionado", # Ou "entrada_inicial"
#         feira_id=db_estoque.feira_id, # Presume que feira_id está em db_estoque
#         observacao="Registro inicial de estoque",
#         # venda_id e item_venda_id seriam None aqui
#         # data_movimentacao será preenchida pelo default do modelo SQLAlchemy
#     )
#     db.add(movimentacao)
#     db.commit() # Segundo commit para a movimentação

#     return db_estoque

# def update_estoque(db: Session, estoque_id: int, estoque: EstoqueCreate) -> Estoque | None:
#     """
#     Atualiza um item de estoque e registra uma movimentação para qualquer atualização via PUT.
#     """
#     db_estoque = get_estoque(db, estoque_id=estoque_id)
#     if not db_estoque:
#         return None

#     quantidade_anterior = db_estoque.quantidade

#     update_data = estoque.model_dump() 
#     for key, value in update_data.items():
#         setattr(db_estoque, key, value)
    
#     quantidade_nova = db_estoque.quantidade
#     quantidade_diferenca = quantidade_nova - quantidade_anterior
    
#     tipo_movimentacao_log = "atualizacao_dados" 
#     if quantidade_diferenca > 0:
#         tipo_movimentacao_log = "ajuste_entrada_manual"
#     elif quantidade_diferenca < 0:
#         tipo_movimentacao_log = "ajuste_saida_manual"
    
#     movimentacao_schema = MovimentacaoEstoqueCreate(
#         produto_id=db_estoque.produto_id,
#         estoque_id=estoque_id,
#         quantidade_alterada=quantidade_diferenca,
#         tipo_movimentacao=tipo_movimentacao_log,
#         feira_id=db_estoque.feira_id, 
#         observacao=f"Atualização do item de estoque ID {estoque_id} via endpoint PUT.",
#     )
#     create_movimentacao_estoque(db=db, movimentacao=movimentacao_schema) # create_movimentacao_estoque não faz commit
    
#     db.commit() # Commit único para as alterações no estoque e a nova movimentação
#     db.refresh(db_estoque)
#     return db_estoque

# def delete_estoque(db: Session, estoque_id: int):
#     db_estoque = db.query(Estoque).filter(Estoque.estoque_id == estoque_id).first()
#     if db_estoque:
#         # Registrar movimentação antes de deletar
#         movimentacao = MovimentacaoEstoque(
#             produto_id=db_estoque.produto_id,
#             estoque_id=db_estoque.estoque_id,
#             quantidade_alterada=-db_estoque.quantidade,
#             tipo_movimentacao="Remoção de Estoque",
#             feira_id=db_estoque.feira_id if hasattr(db_estoque, "feira_id") else None,
#             observacao="Estoque removido do sistema",
#         )
#         db.add(movimentacao)
#         db.commit()

#         # Deletar o estoque
#         db.delete(db_estoque)
#         db.commit()

#     return db_estoque
