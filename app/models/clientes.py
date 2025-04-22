from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship
from app.database import Base

class Cliente(Base):
    __tablename__ = "clientes"

    cliente_id = Column(Integer, primary_key=True, index=True)
    tipo_pessoa = Column(String(20), nullable=False)
    documento = Column(String(20), unique=True, nullable=False)
    nome = Column(String(100), nullable=False)
    email = Column(String(100), index=True)
    endereco = Column(Text)

    vendas = relationship("Venda", back_populates="cliente")
