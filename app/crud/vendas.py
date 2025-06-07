from sqlalchemy.orm import Session, joinedload, selectinload
from sqlalchemy import func
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
    
    return db_venda

def consolidar_venda_e_retornar_estoque(db: Session, venda_id: int) -> dict:
    """
    Consolida as vendas e o estoque de uma feira a partir de uma venda de referência, retornando o que não foi vendido para a Sede.
    """
    
    # 1. Valida a venda de referência e obtém a feira_id
    venda_referencia = db.query(models.Venda).options(joinedload(models.Venda.feira)).filter(models.Venda.venda_id == venda_id).first()
    if not venda_referencia:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Venda com ID {venda_id} não encontrada.")
    
    if not venda_referencia.feira_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=f"A Venda com ID {venda_id} não está associada a nenhuma feira e não pode ser usada para consolidação."
        )
    
    feira_id = venda_referencia.feira_id
    feira = venda_referencia.feira

    # 2. Verifica se esta feira já foi consolidada para evitar duplicidade
    estoque_ja_consolidado = db.query(models.Estoque).filter(
        models.Estoque.feira_id == feira_id,
        models.Estoque.venda_consolidada == True
    ).first()
    if estoque_ja_consolidado:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, 
            detail=f"A Feira com ID {feira_id} (associada à Venda {venda_id}) já foi consolidada anteriormente."
        )

    # 3. Busca e totaliza os produtos vendidos na feira
    itens_vendidos_query = db.query(
        models.Produto.produto_id,
        models.Produto.nome,
        func.sum(models.ItemVenda.quantidade).label("quantidade_total_vendida"),
        func.sum(models.ItemVenda.quantidade * models.ItemVenda.preco_unitario).label("valor_total_arrecadado")
    ).select_from(models.Venda).join(
        models.ItemVenda, models.Venda.venda_id == models.ItemVenda.venda_id
    ).join(
        models.Estoque, models.ItemVenda.estoque_id == models.Estoque.estoque_id
    ).join(
        models.Produto, models.Estoque.produto_id == models.Produto.produto_id
    ).filter(
        models.Venda.feira_id == feira_id
    ).group_by(
        models.Produto.produto_id,
        models.Produto.nome
    ).all()

    produtos_vendidos_info = [
        {
            "produto_id": row.produto_id,
            "nome_produto": row.nome,
            "quantidade_total_vendida": row.quantidade_total_vendida or 0,
            "valor_total_arrecadado": float(row.valor_total_arrecadado or 0.0)
        } for row in itens_vendidos_query
    ]

    # 4. Processa o retorno do estoque não vendido
    estoques_a_retornar = db.query(models.Estoque)\
        .join(models.Estoque.produto)\
        .filter(
            models.Estoque.feira_id == feira_id,
            models.Estoque.quantidade > 0
        ).with_for_update().all()

    produtos_retornados_info = []
    for estoque_feira in estoques_a_retornar:
        quantidade_a_retornar = estoque_feira.quantidade
        produto_id = estoque_feira.produto_id

        estoque_sede = db.query(models.Estoque).filter(
            models.Estoque.produto_id == produto_id,
            models.Estoque.feira_id.is_(None),
            models.Estoque.localizacao == "Sede"
        ).with_for_update().first()

        if not estoque_sede:
            estoque_sede = models.Estoque(produto_id=produto_id, quantidade=0, localizacao="Sede", data_atualizacao=datetime.utcnow())
            db.add(estoque_sede)
            db.flush()
        
        mov_saida_feira = models.MovimentacaoEstoque(produto_id=produto_id, estoque_id=estoque_feira.estoque_id, quantidade_alterada=-quantidade_a_retornar, tipo_movimentacao='RETORNO_DE_FEIRA_SAIDA', feira_id=feira_id, observacao=f"Retorno de {quantidade_a_retornar} unidades da feira '{feira.nome}' para a Sede.")
        db.add(mov_saida_feira)

        mov_entrada_sede = models.MovimentacaoEstoque(produto_id=produto_id, estoque_id=estoque_sede.estoque_id, quantidade_alterada=quantidade_a_retornar, tipo_movimentacao='RETORNO_DE_FEIRA_ENTRADA', feira_id=feira_id, observacao=f"Entrada de {quantidade_a_retornar} unidades na Sede, da feira '{feira.nome}'.")
        db.add(mov_entrada_sede)

        estoque_sede.quantidade += quantidade_a_retornar
        estoque_sede.data_atualizacao = datetime.utcnow()
        estoque_feira.quantidade = 0
        estoque_feira.data_atualizacao = datetime.utcnow()
        
        produtos_retornados_info.append({
            "produto_id": produto_id, "nome_produto": estoque_feira.produto.nome, "quantidade_retornada": quantidade_a_retornar,
            "estoque_feira_id_zerado": estoque_feira.estoque_id, "estoque_sede_id_atualizado": estoque_sede.estoque_id,
            "nova_quantidade_sede": estoque_sede.quantidade
        })

    # 5. Marca TODOS os itens de estoque da feira como consolidados
    db.query(models.Estoque)\
        .filter(models.Estoque.feira_id == feira_id)\
        .update({"venda_consolidada": True}, synchronize_session=False)

    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Ocorreu um erro ao consolidar a feira: {str(e)}")
    
    return {
        "message": f"Estoque da feira ID {feira_id} consolidado e retornado para a Sede com sucesso.",
        "feira_id": feira_id,
        "produtos_vendidos": produtos_vendidos_info,
        "produtos_retornados": produtos_retornados_info
    }
