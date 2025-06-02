from sqlalchemy.orm import Session
from datetime import date
from .. import models, schemas



def get_feira(db: Session, feira_id: int):
    """Busca uma única feira pelo seu ID."""
    return db.query(models.Feira).filter(models.Feira.feira_id == feira_id).first()

def get_feira_by_name(db: Session, nome: str):
    """Busca uma única feira pelo seu nome."""
    return db.query(models.Feira).filter(models.Feira.nome == nome).first()

def get_feiras(db: Session, skip: int = 0, limit: int = 100):
    """Busca uma lista de feiras com paginação."""
    return db.query(models.Feira).offset(skip).limit(limit).all()

def get_feira_by_name_and_date(db: Session, nome: str, data_feira: date):
    """
    Busca uma feira pelo nome e data.
    """
    return db.query(models.Feira).filter(models.Feira.nome == nome, models.Feira.data == data_feira).first()

def create_feira(db: Session, feira: schemas.FeiraCreate):
    """Cria uma nova feira no banco de dados."""

    db_feira = models.Feira(
        nome=feira.nome,
        data=feira.data  
    )
    db.add(db_feira)
    db.commit()
    db.refresh(db_feira)
    return db_feira

def update_feira(db: Session, feira_id: int, feira: schemas.FeiraCreate):
    """Atualiza uma feira no banco de dados."""
    db_feira = db.query(models.Feira).filter(models.Feira.feira_id == feira_id).first()
    if db_feira:
        db_feira.nome = feira.nome
        db_feira.data = feira.data
        db.commit()
        db.refresh(db_feira)
    return db_feira

def delete_feira(db: Session, feira_id: int):
    """Deleta uma feira do banco de dados."""
    db_feira = db.query(models.Feira).filter(models.Feira.feira_id == feira_id).first()
    if db_feira:
        db.delete(db_feira)
        db.commit()
    return db_feira

