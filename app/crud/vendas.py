from sqlalchemy.orm import Session
from app.models import Venda, ItemVenda
from app.schemas import VendaCreate
from app import crud

def get_vendas(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Venda).offset(skip).limit(limit).all()

def get_venda(db: Session, venda_id: int):
    return db.query(Venda).filter(Venda.venda_id == venda_id).first()

def create_venda(db: Session, venda: VendaCreate):
    """
    Cria uma nova venda e seus itens associados no banco de dados.
    O campo 'feira_id' é opcional e será incluído se presente no objeto 'venda'.
    """
    
    db_venda = Venda(**venda.dict(exclude={'itens_venda'})) 
    
    db.add(db_venda)
    db.commit() 
    db.refresh(db_venda) 

    
    for item_data in venda.itens_venda:
      
        db_item_venda = ItemVenda(
            venda_id=db_venda.venda_id,
            produto_id=item_data.produto_id,
            quantidade=item_data.quantidade,
            preco_unitario=item_data.preco_unitario,
            subtotal=item_data.subtotal 
        )
        db.add(db_item_venda)
    
    db.commit()
    db.refresh(db_venda)

    return db_venda

def update_venda(db: Session, venda_id: int, venda: VendaCreate):
    db_venda = db.query(Venda).filter(Venda.venda_id == venda_id).first()
    if db_venda:
        for key, value in venda.dict().items():
            setattr(db_venda, key, value)
        db.commit()
        db.refresh(db_venda)
    return db_venda

def delete_venda(db: Session, venda_id: int):
    db_venda = db.query(Venda).filter(Venda.venda_id == venda_id).first()
    if db_venda:
        db.delete(db_venda)
        db.commit()
    return db_venda
