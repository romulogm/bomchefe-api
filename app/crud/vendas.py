from sqlalchemy.orm import Session, joinedload, selectinload
from fastapi import HTTPException, status
from datetime import datetime
from .. import models, schemas

# Funções get_vendas e get_venda permanecem as mesmas
def get_vendas(db: Session, skip: int = 0, limit: int = 100) -> list[schemas.Venda]:
    """
    Retorna uma lista de vendas, carregando os relacionamentos 'feira', 'itens_venda',
    e o 'produto' de cada item através do estoque.
    """
    return db.query(models.Venda)\
             .options(
                 joinedload(models.Venda.feira), 
                 selectinload(models.Venda.itens_venda) 
                     .joinedload(models.ItemVenda.item_de_estoque_utilizado) 
                     .joinedload(models.Estoque.produto) 
             )\
             .offset(skip)\
             .limit(limit)\
             .all()

def get_venda(db: Session, venda_id: int) -> schemas.Venda | None:
    """
    Retorna uma venda específica pelo ID, carregando os relacionamentos 'feira', 'itens_venda',
    e o 'produto' de cada item através do estoque.
    """
    return db.query(models.Venda)\
             .options(
                 joinedload(models.Venda.feira), 
                 selectinload(models.Venda.itens_venda) 
                     .joinedload(models.ItemVenda.item_de_estoque_utilizado) 
                     .joinedload(models.Estoque.produto) 
             )\
             .filter(models.Venda.venda_id == venda_id)\
             .first()

def create_venda(db: Session, venda_data: schemas.VendaCreate) -> models.Venda: # Retorna o modelo SQLAlchemy
    """
    Cria uma nova venda, seus itens, deduz do estoque e registra movimentações.
    """
    
    # 1. Prepara e cria o objeto Venda principal
    venda_dict = venda_data.model_dump(exclude={'itens_venda'}) 
    db_venda = models.Venda(**venda_dict) 
    db.add(db_venda)
    db.flush() 

    # 2. Processa cada item da venda
    if not venda_data.itens_venda:
        db.rollback() # Desfaz a criação da venda se não houver itens
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A venda deve conter pelo menos um item."
        )

    for item_data in venda_data.itens_venda:
        db_estoque = db.query(models.Estoque).filter(models.Estoque.estoque_id == item_data.estoque_id).with_for_update().first() # Lock para atualização

        if not db_estoque:
            db.rollback() 
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Estoque com ID {item_data.estoque_id} não encontrado."
            )

        if db_venda.feira_id and db_estoque.feira_id != db_venda.feira_id:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"O item de estoque ID {db_estoque.estoque_id} (Produto ID: {db_estoque.produto_id}) não pertence à feira ID {db_venda.feira_id} desta venda."
            )
        
        if db_estoque.quantidade < item_data.quantidade:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, 
                detail=f"Estoque insuficiente para o produto ID {db_estoque.produto_id} (Estoque ID: {db_estoque.estoque_id}). Disponível: {db_estoque.quantidade}, Solicitado: {item_data.quantidade}."
            )

        db_estoque.quantidade -= item_data.quantidade
        db_estoque.data_atualizacao = datetime.utcnow()

        db_item_venda = models.ItemVenda(
            venda_id=db_venda.venda_id,
            estoque_id=item_data.estoque_id,
            quantidade=item_data.quantidade, 
            preco_unitario=item_data.preco_unitario 
        )
        db.add(db_item_venda)
        db.flush() 

        movimentacao = models.MovimentacaoEstoque(
            produto_id=db_estoque.produto_id,
            estoque_id=db_estoque.estoque_id,
            quantidade_alterada=-item_data.quantidade, 
            tipo_movimentacao='SAIDA_VENDA_FEIRA' if db_venda.feira_id else 'SAIDA_VENDA_SEDE',
            feira_id=db_venda.feira_id, 
            venda_id=db_venda.venda_id,
            item_venda_id=db_item_venda.item_venda_id,
            observacao=f"Venda do item ID {db_item_venda.item_venda_id} (Produto ID: {db_estoque.produto_id})"
        )
        db.add(movimentacao)
    
    try:
        db.commit()
    except Exception as e: 
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ocorreu um erro ao tentar salvar a venda: {str(e)}"
        )
    
    db.refresh(db_venda)
    venda_completa = db.query(models.Venda)\
                       .options(
                           joinedload(models.Venda.feira),
                           selectinload(models.Venda.itens_venda)
                               .joinedload(models.ItemVenda.item_de_estoque_utilizado)
                               .joinedload(models.Estoque.produto)
                       )\
                       .filter(models.Venda.venda_id == db_venda.venda_id)\
                       .first()
    
    if not venda_completa: 
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Venda criada mas não pôde ser recarregada.")

    return venda_completa

def update_venda(db: Session, venda_id: int, venda_data: schemas.VendaUpdate) -> models.Venda | None:
    """
    Atualiza uma venda existente.
    Se 'itens_venda' for fornecido no payload, os itens existentes são substituídos.
    """
    db_venda = db.query(models.Venda).filter(models.Venda.venda_id == venda_id).first()
    if not db_venda:
        return None

    # 1. Atualiza campos escalares da Venda
    update_data_scalar = venda_data.model_dump(exclude_unset=True, exclude={'itens_venda'})
    for key, value in update_data_scalar.items():
        setattr(db_venda, key, value)
    
    # 2. Lida com a atualização dos itens_venda, se fornecido
    if venda_data.itens_venda is not None: # Permite enviar lista vazia para remover todos os itens
        # a. Retorna ao estoque e registra movimentação para itens antigos
        for old_item in list(db_venda.itens_venda): # Itera sobre uma cópia
            db_estoque_antigo = db.query(models.Estoque).filter(models.Estoque.estoque_id == old_item.estoque_id).with_for_update().first()
            if db_estoque_antigo:
                db_estoque_antigo.quantidade += old_item.quantidade
                db_estoque_antigo.data_atualizacao = datetime.utcnow()
                
                mov_retorno = models.MovimentacaoEstoque(
                    produto_id=db_estoque_antigo.produto_id,
                    estoque_id=db_estoque_antigo.estoque_id,
                    quantidade_alterada=old_item.quantidade, # Positivo para retorno
                    tipo_movimentacao='RETORNO_ATUALIZACAO_VENDA',
                    feira_id=db_venda.feira_id,
                    venda_id=db_venda.venda_id,
                    item_venda_id=old_item.item_venda_id, # Referencia o item antigo
                    observacao=f"Retorno ao estoque devido à atualização da venda ID {db_venda.venda_id}, item ID {old_item.item_venda_id}"
                )
                db.add(mov_retorno)
            db.delete(old_item) # Marca o item antigo para deleção
        
        db.flush() # Processa deleções e atualizações de estoque dos itens antigos

        # b. Adiciona novos itens (lógica similar à create_venda)
        for new_item_data in venda_data.itens_venda:
            db_estoque_novo = db.query(models.Estoque).filter(models.Estoque.estoque_id == new_item_data.estoque_id).with_for_update().first()
            if not db_estoque_novo:
                db.rollback()
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Estoque com ID {new_item_data.estoque_id} não encontrado para novo item.")
            
            if db_venda.feira_id and db_estoque_novo.feira_id != db_venda.feira_id:
                db.rollback()
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"O novo item de estoque ID {db_estoque_novo.estoque_id} não pertence à feira ID {db_venda.feira_id}."
                )

            if db_estoque_novo.quantidade < new_item_data.quantidade:
                db.rollback()
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Estoque insuficiente para novo item (Produto ID: {db_estoque_novo.produto_id}).")

            db_estoque_novo.quantidade -= new_item_data.quantidade
            db_estoque_novo.data_atualizacao = datetime.utcnow()

            db_new_item_venda = models.ItemVenda(
                venda_id=db_venda.venda_id,
                estoque_id=new_item_data.estoque_id,
                quantidade=new_item_data.quantidade,
                preco_unitario=new_item_data.preco_unitario
            )
            db.add(db_new_item_venda) # Adiciona à sessão, será associado à venda
            db.flush()

            mov_saida = models.MovimentacaoEstoque(
                produto_id=db_estoque_novo.produto_id,
                estoque_id=db_estoque_novo.estoque_id,
                quantidade_alterada=-new_item_data.quantidade,
                tipo_movimentacao='SAIDA_VENDA_FEIRA_ATUALIZADA' if db_venda.feira_id else 'SAIDA_VENDA_SEDE_ATUALIZADA',
                feira_id=db_venda.feira_id,
                venda_id=db_venda.venda_id,
                item_venda_id=db_new_item_venda.item_venda_id,
                observacao=f"Venda atualizada, item ID {db_new_item_venda.item_venda_id}"
            )
            db.add(mov_saida)

    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ocorreu um erro ao tentar atualizar a venda: {str(e)}"
        )

    db.refresh(db_venda)
    venda_atualizada_completa = db.query(models.Venda)\
                               .options(
                                   joinedload(models.Venda.feira),
                                   selectinload(models.Venda.itens_venda)
                                       .joinedload(models.ItemVenda.item_de_estoque_utilizado)
                                       .joinedload(models.Estoque.produto)
                               )\
                               .filter(models.Venda.venda_id == db_venda.venda_id)\
                               .first()
    return venda_atualizada_completa

def delete_venda(db: Session, venda_id: int) -> models.Venda | None:
    """
    Deleta uma venda existente, retorna as quantidades ao estoque e registra movimentações.
    """
    db_venda = db.query(models.Venda)\
                 .options(selectinload(models.Venda.itens_venda) # Carrega os itens para processamento
                              .joinedload(models.ItemVenda.item_de_estoque_utilizado))\
                 .filter(models.Venda.venda_id == venda_id)\
                 .first()

    if not db_venda:
        return None
    # 1. Retorna itens ao estoque e registra movimentações
    for item_venda in list(db_venda.itens_venda): # Itera sobre uma cópia
        db_estoque = item_venda.item_de_estoque_utilizado # Já carregado
        if db_estoque:
            db_estoque.quantidade += item_venda.quantidade
            db_estoque.data_atualizacao = datetime.utcnow()

            mov_retorno = models.MovimentacaoEstoque(
                produto_id=db_estoque.produto_id,
                estoque_id=db_estoque.estoque_id,
                quantidade_alterada=item_venda.quantidade, # Positivo para retorno
                tipo_movimentacao='RETORNO_CANCELAMENTO_VENDA',
                feira_id=db_venda.feira_id,
                venda_id=db_venda.venda_id,
                item_venda_id=item_venda.item_venda_id,
                observacao=f"Retorno ao estoque devido ao cancelamento da venda ID {db_venda.venda_id}, item ID {item_venda.item_venda_id}"
            )
            db.add(mov_retorno)
        # Não é necessário deletar item_venda explicitamente aqui,
        # pois o cascade="all, delete-orphan" em Venda.itens_venda fará isso.
        # Mas é importante que o processamento do estoque ocorra antes do commit final.
    
    # 2. Deleta a Venda (o cascade cuidará dos ItemVenda)
    db.delete(db_venda)
    
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ocorreu um erro ao tentar deletar a venda: {str(e)}"
        )
    
    # O objeto db_venda está agora desanexado e marcado como deletado.
    # Retorná-lo pode ser útil para confirmar a deleção, mas ele não estará mais na sessão.
    return db_venda
# from sqlalchemy.orm import Session, joinedload, selectinload # Importe joinedload e selectinload
# from .. import models, schemas

# def get_vendas(db: Session, skip: int = 0, limit: int = 100) -> list[schemas.Venda]:
#     """
#     Retorna uma lista de vendas, carregando os relacionamentos 'feira', 'itens_venda',
#     e o 'produto' de cada item através do estoque.
#     """
#     return db.query(models.Venda)\
#              .options(
#                  joinedload(models.Venda.feira), # Carrega os dados da feira
#                  selectinload(models.Venda.itens_venda) # Carrega a lista de itens_venda
#                      .joinedload(models.ItemVenda.item_de_estoque_utilizado) # A partir de ItemVenda, carrega o Estoque
#                      .joinedload(models.Estoque.produto) # A partir de Estoque, carrega o Produto
#              )\
#              .offset(skip)\
#              .limit(limit)\
#              .all()

# def get_venda(db: Session, venda_id: int) -> schemas.Venda | None:
#     """
#     Retorna uma venda específica pelo ID, carregando os relacionamentos 'feira', 'itens_venda',
#     e o 'produto' de cada item através do estoque.
#     """
#     return db.query(models.Venda)\
#              .options(
#                  joinedload(models.Venda.feira), # Carrega os dados da feira
#                  selectinload(models.Venda.itens_venda) # Carrega a lista de itens_venda
#                      .joinedload(models.ItemVenda.item_de_estoque_utilizado) # A partir de ItemVenda, carrega o Estoque
#                      .joinedload(models.Estoque.produto) # A partir de Estoque, carrega o Produto
#              )\
#              .filter(models.Venda.venda_id == venda_id)\
#              .first()

# def create_venda(db: Session, venda_data: schemas.VendaCreate) -> schemas.Venda:
#     """
#     Cria uma nova venda e seus itens associados no banco de dados em uma única transação.
#     O campo 'feira_id' é opcional e será incluído se presente no objeto 'venda_data'.
#     """
    
#     # 1. Prepara o dicionário para criar a Venda, excluindo os itens por enquanto
#     venda_dict = venda_data.model_dump(exclude={'itens_venda'}) 
    
#     db_venda = models.Venda(**venda_dict) 
    
#     db.add(db_venda)
    
#     # 2. Força o SQLAlchemy a executar a inserção da Venda para obter o venda_id
#     # Isso é crucial antes de adicionar os itens de venda.
#     db.flush() 

#     # 3. Itera sobre os itens de venda fornecidos e os adiciona à sessão
#     if venda_data.itens_venda: # Verifica se há itens para adicionar
#         for item_data in venda_data.itens_venda:
#             # Use .model_dump() para Pydantic v2+, ou .dict() para Pydantic v1
#             # Mapeia os campos do schema ItemVendaCreate para o modelo ItemVenda
#             db_item_venda = models.ItemVenda(
#                 venda_id=db_venda.venda_id, # Usa o ID da venda recém-criada
#                 estoque_id=item_data.estoque_id, # Do schema ItemVendaCreate
#                 quantidade=item_data.quantidade, # Do schema ItemVendaCreate
#                 preco_unitario=item_data.preco_unitario # Do schema ItemVendaCreate
#             )
#             db.add(db_item_venda)
    
#     # 4. Comita todas as alterações (venda e itens) de uma vez
#     db.commit()
    
#     # 5. Atualiza o objeto db_venda para refletir os itens recém-adicionados
#     # e outros dados gerados pelo banco (como data_venda se default=datetime.utcnow)
#     db.refresh(db_venda)

#     # 6. Carrega os relacionamentos para que o objeto retornado inclua feira e itens_venda com seus produtos
#     # Isso garante que a resposta da API contenha os dados completos
#     # É importante buscar novamente ou garantir que a sessão tenha os dados carregados.
#     # Uma forma segura é buscar novamente o objeto com os options desejados.
#     venda_completa = db.query(models.Venda)\
#                        .options(
#                            joinedload(models.Venda.feira),
#                            selectinload(models.Venda.itens_venda)
#                                .joinedload(models.ItemVenda.item_de_estoque_utilizado)
#                                .joinedload(models.Estoque.produto)
#                        )\
#                        .filter(models.Venda.venda_id == db_venda.venda_id)\
#                        .first()

#     return venda_completa

# def update_venda(db: Session, venda_id: int, venda_data: schemas.VendaUpdate) -> schemas.Venda | None: # Alterado para VendaUpdate
#     """
#     Atualiza uma venda existente no banco de dados.
#     A atualização de itens de venda é mais complexa e não está totalmente implementada aqui.
#     Esta função focará em atualizar os campos diretos da Venda.
#     """
#     db_venda = db.query(models.Venda).filter(models.Venda.venda_id == venda_id).first()
#     if db_venda:
#         # Atualiza os campos diretos da Venda
#         # Use .model_dump(exclude_unset=True) para Pydantic v2+ para permitir atualizações parciais
#         update_data = venda_data.model_dump(exclude_unset=True, exclude={'itens_venda'}) 
#         for key, value in update_data.items():
#             setattr(db_venda, key, value)
        
#         # AVISO: A lógica para atualizar 'itens_venda' é mais complexa.
#         # Se 'venda_data.itens_venda' for fornecido, você precisaria implementar
#         # uma lógica para adicionar/remover/atualizar itens.
#         # Por simplicidade, esta parte é omitida.

#         db.commit()
#         db.refresh(db_venda)
        
#         # Recarrega com relacionamentos para a resposta
#         venda_atualizada_completa = db.query(models.Venda)\
#                                    .options(
#                                        joinedload(models.Venda.feira),
#                                        selectinload(models.Venda.itens_venda)
#                                            .joinedload(models.ItemVenda.item_de_estoque_utilizado)
#                                            .joinedload(models.Estoque.produto)
#                                    )\
#                                    .filter(models.Venda.venda_id == db_venda.venda_id)\
#                                    .first()
#         return venda_atualizada_completa
#     return None # Retorna None se a venda não for encontrada

# def delete_venda(db: Session, venda_id: int) -> models.Venda | None:
#     """
#     Deleta uma venda existente e, devido ao cascade="all, delete-orphan",
#     também deleta seus itens de venda associados.
#     """
#     db_venda = db.query(models.Venda).filter(models.Venda.venda_id == venda_id).first()
#     if db_venda:
#         db.delete(db_venda)
#         db.commit()
#     return db_venda
