from sqlalchemy.orm import Session, joinedload, selectinload # Importe joinedload e selectinload
from .. import models, schemas

def get_vendas(db: Session, skip: int = 0, limit: int = 100) -> list[schemas.Venda]:
    """
    Retorna uma lista de vendas, carregando os relacionamentos 'feira', 'itens_venda',
    e o 'produto' de cada item através do estoque.
    """
    return db.query(models.Venda)\
             .options(
                 joinedload(models.Venda.feira), # Carrega os dados da feira
                 selectinload(models.Venda.itens_venda) # Carrega a lista de itens_venda
                     .joinedload(models.ItemVenda.item_de_estoque_utilizado) # A partir de ItemVenda, carrega o Estoque
                     .joinedload(models.Estoque.produto) # A partir de Estoque, carrega o Produto
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
                 joinedload(models.Venda.feira), # Carrega os dados da feira
                 selectinload(models.Venda.itens_venda) # Carrega a lista de itens_venda
                     .joinedload(models.ItemVenda.item_de_estoque_utilizado) # A partir de ItemVenda, carrega o Estoque
                     .joinedload(models.Estoque.produto) # A partir de Estoque, carrega o Produto
             )\
             .filter(models.Venda.venda_id == venda_id)\
             .first()

def create_venda(db: Session, venda_data: schemas.VendaCreate) -> schemas.Venda:
    """
    Cria uma nova venda e seus itens associados no banco de dados em uma única transação.
    O campo 'feira_id' é opcional e será incluído se presente no objeto 'venda_data'.
    """
    
    # 1. Prepara o dicionário para criar a Venda, excluindo os itens por enquanto
    venda_dict = venda_data.model_dump(exclude={'itens_venda'}) 
    
    db_venda = models.Venda(**venda_dict) 
    
    db.add(db_venda)
    
    # 2. Força o SQLAlchemy a executar a inserção da Venda para obter o venda_id
    # Isso é crucial antes de adicionar os itens de venda.
    db.flush() 

    # 3. Itera sobre os itens de venda fornecidos e os adiciona à sessão
    if venda_data.itens_venda: # Verifica se há itens para adicionar
        for item_data in venda_data.itens_venda:
            # Use .model_dump() para Pydantic v2+, ou .dict() para Pydantic v1
            # Mapeia os campos do schema ItemVendaCreate para o modelo ItemVenda
            db_item_venda = models.ItemVenda(
                venda_id=db_venda.venda_id, # Usa o ID da venda recém-criada
                estoque_id=item_data.estoque_id, # Do schema ItemVendaCreate
                quantidade=item_data.quantidade, # Do schema ItemVendaCreate
                preco_unitario=item_data.preco_unitario # Do schema ItemVendaCreate
            )
            db.add(db_item_venda)
    
    # 4. Comita todas as alterações (venda e itens) de uma vez
    db.commit()
    
    # 5. Atualiza o objeto db_venda para refletir os itens recém-adicionados
    # e outros dados gerados pelo banco (como data_venda se default=datetime.utcnow)
    db.refresh(db_venda)

    # 6. Carrega os relacionamentos para que o objeto retornado inclua feira e itens_venda com seus produtos
    # Isso garante que a resposta da API contenha os dados completos
    # É importante buscar novamente ou garantir que a sessão tenha os dados carregados.
    # Uma forma segura é buscar novamente o objeto com os options desejados.
    venda_completa = db.query(models.Venda)\
                       .options(
                           joinedload(models.Venda.feira),
                           selectinload(models.Venda.itens_venda)
                               .joinedload(models.ItemVenda.item_de_estoque_utilizado)
                               .joinedload(models.Estoque.produto)
                       )\
                       .filter(models.Venda.venda_id == db_venda.venda_id)\
                       .first()

    return venda_completa

def update_venda(db: Session, venda_id: int, venda_data: schemas.VendaUpdate) -> schemas.Venda | None: # Alterado para VendaUpdate
    """
    Atualiza uma venda existente no banco de dados.
    A atualização de itens de venda é mais complexa e não está totalmente implementada aqui.
    Esta função focará em atualizar os campos diretos da Venda.
    """
    db_venda = db.query(models.Venda).filter(models.Venda.venda_id == venda_id).first()
    if db_venda:
        # Atualiza os campos diretos da Venda
        # Use .model_dump(exclude_unset=True) para Pydantic v2+ para permitir atualizações parciais
        update_data = venda_data.model_dump(exclude_unset=True, exclude={'itens_venda'}) 
        for key, value in update_data.items():
            setattr(db_venda, key, value)
        
        # AVISO: A lógica para atualizar 'itens_venda' é mais complexa.
        # Se 'venda_data.itens_venda' for fornecido, você precisaria implementar
        # uma lógica para adicionar/remover/atualizar itens.
        # Por simplicidade, esta parte é omitida.

        db.commit()
        db.refresh(db_venda)
        
        # Recarrega com relacionamentos para a resposta
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
    return None # Retorna None se a venda não for encontrada

def delete_venda(db: Session, venda_id: int) -> models.Venda | None:
    """
    Deleta uma venda existente e, devido ao cascade="all, delete-orphan",
    também deleta seus itens de venda associados.
    """
    db_venda = db.query(models.Venda).filter(models.Venda.venda_id == venda_id).first()
    if db_venda:
        db.delete(db_venda)
        db.commit()
    return db_venda
