# from sqlalchemy.orm import Session
# from app.models import Venda, ItemVenda
# from app.schemas import VendaCreate
# from app import crud

# def get_vendas(db: Session, skip: int = 0, limit: int = 100):
#     return db.query(Venda).offset(skip).limit(limit).all()

# def get_venda(db: Session, venda_id: int):
#     return db.query(Venda).filter(Venda.venda_id == venda_id).first()

# def create_venda(db: Session, venda: VendaCreate):
#     """
#     Cria uma nova venda e seus itens associados no banco de dados.
#     O campo 'feira_id' é opcional e será incluído se presente no objeto 'venda'.
#     """
    
#     db_venda = Venda(**venda.dict(exclude={'itens_venda'})) 
    
#     db.add(db_venda)
#     db.commit() 
#     db.refresh(db_venda) 

    
#     for item_data in venda.itens_venda:
      
#         db_item_venda = ItemVenda(
#             venda_id=db_venda.venda_id,
#             produto_id=item_data.produto_id,
#             quantidade=item_data.quantidade,
#             preco_unitario=item_data.preco_unitario,
#             subtotal=item_data.subtotal 
#         )
#         db.add(db_item_venda)
    
#     db.commit()
#     db.refresh(db_venda)

#     return db_venda

# def update_venda(db: Session, venda_id: int, venda: VendaCreate):
#     db_venda = db.query(Venda).filter(Venda.venda_id == venda_id).first()
#     if db_venda:
#         for key, value in venda.dict().items():
#             setattr(db_venda, key, value)
#         db.commit()
#         db.refresh(db_venda)
#     return db_venda

# def delete_venda(db: Session, venda_id: int):
#     db_venda = db.query(Venda).filter(Venda.venda_id == venda_id).first()
#     if db_venda:
#         db.delete(db_venda)
#         db.commit()
#     return db_venda
from sqlalchemy.orm import Session, joinedload # Importe joinedload para carregar relacionamentos
from app.models import Venda, ItemVenda, Feira, Produto # Certifique-se de importar todos os modelos necessários
from app.schemas import VendaCreate, Venda # Importe o schema Venda para tipagem de retorno

# Importe os schemas de ItemVenda e Feira também, se forem usados diretamente aqui
from app.schemas import ItemVendaBase # Assumindo que ItemVendaBase e ItemVenda estão em schemas/venda.py
from app.schemas import Feira as FeiraSchema # Importe o schema Feira como FeiraSchema para evitar conflito de nome

def get_vendas(db: Session, skip: int = 0, limit: int = 100):
    """
    Retorna uma lista de vendas, carregando os relacionamentos 'feira' e 'itens_venda'.
    """
    return db.query(Venda)\
             .options(
                 joinedload(Venda.feira), # Carrega os dados da feira
                 joinedload(Venda.itens_venda).joinedload(ItemVenda.produto) # Carrega os itens e seus produtos
             )\
             .offset(skip)\
             .limit(limit)\
             .all()

def get_venda(db: Session, venda_id: int):
    """
    Retorna uma venda específica pelo ID, carregando os relacionamentos 'feira' e 'itens_venda'.
    """
    return db.query(Venda)\
             .options(
                 joinedload(Venda.feira), # Carrega os dados da feira
                 joinedload(Venda.itens_venda).joinedload(ItemVenda.produto) # Carrega os itens e seus produtos
             )\
             .filter(Venda.venda_id == venda_id)\
             .first()

def create_venda(db: Session, venda_data: VendaCreate) -> Venda: # Adicionei a tipagem de retorno
    """
    Cria uma nova venda e seus itens associados no banco de dados em uma única transação.
    O campo 'feira_id' é opcional e será incluído se presente no objeto 'venda_data'.
    """
    
    # 1. Extrai os dados da venda principal, excluindo a lista de itens
    # Use .model_dump() para Pydantic v2+, ou .dict() para Pydantic v1
    venda_dict = venda_data.model_dump(exclude={'itens_venda'}) 
    
    db_venda = Venda(**venda_dict) 
    
    db.add(db_venda)
    
    # 2. Força o SQLAlchemy a executar a inserção da Venda para obter o venda_id
    # Isso é crucial antes de adicionar os itens de venda.
    db.flush() 

    # 3. Itera sobre os itens de venda fornecidos e os adiciona à sessão
    for item_data in venda_data.itens_venda:
        # Use .model_dump() para Pydantic v2+, ou .dict() para Pydantic v1
        item_dict = item_data.model_dump()
        
        # Cria a instância de ItemVenda, vinculando-a ao venda_id recém-gerado
        db_item_venda = ItemVenda(
            venda_id=db_venda.venda_id, # Usa o ID da venda recém-criada
            **item_dict # Desempacota os outros campos do item
        )
        db.add(db_item_venda)
    
    # 4. Comita todas as alterações (venda e itens) de uma vez
    db.commit()
    
    # 5. Atualiza o objeto db_venda para refletir os itens recém-adicionados
    # e outros dados gerados pelo banco (como data_venda se default=datetime.utcnow)
    db.refresh(db_venda)

    # 6. Carrega os relacionamentos para que o objeto retornado inclua feira e itens_venda
    # Isso garante que a resposta da API contenha os dados completos
    db_venda = db.query(Venda)\
                 .options(
                     joinedload(Venda.feira),
                     joinedload(Venda.itens_venda).joinedload(ItemVenda.produto)
                 )\
                 .filter(Venda.venda_id == db_venda.venda_id)\
                 .first()

    return db_venda

def update_venda(db: Session, venda_id: int, venda_data: VendaCreate): # Usando VendaCreate para o corpo da requisição
    """
    Atualiza uma venda existente no banco de dados.
    A atualização de itens de venda é mais complexa e não está totalmente implementada aqui.
    """
    db_venda = db.query(Venda).filter(Venda.venda_id == venda_id).first()
    if db_venda:
        # Atualiza os campos diretos da Venda
        # Use .model_dump(exclude_unset=True) para Pydantic v2+ para permitir atualizações parciais
        # ou .dict(exclude_unset=True) para Pydantic v1
        update_data = venda_data.model_dump(exclude_unset=True, exclude={'itens_venda'})
        for key, value in update_data.items():
            setattr(db_venda, key, value)
        
        # AVISO: A lógica para atualizar 'itens_venda' é mais complexa.
        # Geralmente envolve:
        # 1. Comparar os itens existentes com os novos.
        # 2. Deletar itens que não estão mais na lista.
        # 3. Atualizar itens existentes.
        # 4. Criar novos itens.
        # Isso não está implementado nesta função para evitar complexidade excessiva.
        # Se precisar, considere um endpoint PUT/PATCH separado para itens de venda,
        # ou implemente uma lógica de diff aqui.

        db.commit()
        db.refresh(db_venda)
        
        # Recarrega com relacionamentos para a resposta
        db_venda = db.query(Venda)\
                     .options(
                         joinedload(Venda.feira),
                         joinedload(Venda.itens_venda).joinedload(ItemVenda.produto)
                     )\
                     .filter(Venda.venda_id == db_venda.venda_id)\
                     .first()
    return db_venda

def delete_venda(db: Session, venda_id: int):
    """
    Deleta uma venda existente e, devido ao cascade="all, delete-orphan",
    também deleta seus itens de venda associados.
    """
    db_venda = db.query(Venda).filter(Venda.venda_id == venda_id).first()
    if db_venda:
        db.delete(db_venda)
        db.commit()
    return db_venda
