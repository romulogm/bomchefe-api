from sqlalchemy import Column, Integer, String, Date
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

# class Feira(Base):
#     __tablename__ = "feiras"

#     feira_id = Column(Integer, primary_key=True, index=True)
#     nome = Column(String(100), nullable=False, unique=True, index=True)
#     vendas = relationship("Venda", back_populates="feira")

class Feira(Base):
    __tablename__ = "feiras"

    feira_id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False, index=True) 
    data = Column(Date, nullable=False, index=True) 

    itens_de_estoque = relationship("Estoque", back_populates="feira")
    vendas = relationship("Venda", back_populates="feira")
    movimentacoes_estoque = relationship("MovimentacaoEstoque", back_populates="feira")