from sqlalchemy import Column, Integer, ForeignKey, String, DateTime, Numeric
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class Venda(Base):
    __tablename__ = "vendas"

    venda_id = Column(Integer, primary_key=True, index=True)
    data_venda = Column(DateTime, nullable=False, default=datetime.utcnow)
    cliente_id = Column(Integer, ForeignKey("clientes.cliente_id"), nullable=False)
    valor_total = Column(Numeric(10, 2), nullable=False)
    metodo_pagamento = Column(String(50))
    status_venda = Column(String(30), nullable=False, default='Pendente')

    feira_id = Column(Integer, ForeignKey("feiras.feira_id"), nullable=True, index=True)
    feira = relationship("Feira", back_populates="vendas")
    cliente = relationship("Cliente", back_populates="vendas")
    itens_venda = relationship("ItemVenda", back_populates="venda", cascade="all, delete-orphan")



