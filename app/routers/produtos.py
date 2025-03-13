from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Produto

router = APIRouter()

@router.get("/produtos/")
def listar_produtos(db: Session = Depends(get_db)):
    return db.query(Produto).all()

