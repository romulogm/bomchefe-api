from sqlalchemy import Column, Integer, String, Text, Numeric, Boolean, Date
from app.database import Base

class Produto(Base):
    __tablename__ = "produtos"

    produto_id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    descricao = Column(Text)
    categoria = Column(String(50))
    preco_unitario = Column(Numeric(10, 2), nullable=False)
    peso_gramas = Column(Integer)
    data_criacao = Column(Date, nullable=False)
    status = Column(Boolean, default=True, nullable=False)
