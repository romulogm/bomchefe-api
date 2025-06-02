from sqlalchemy import Column, Integer, String, Text, Date, Boolean
from sqlalchemy.types import DECIMAL
from sqlalchemy.orm import relationship
from app.database import Base

class Produto(Base):
    __tablename__ = "produtos"

    produto_id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    descricao = Column(Text)
    categoria = Column(String(50))
    preco_unitario = Column(DECIMAL(10, 2), nullable=False)
    peso_gramas = Column(Integer)
    data_criacao = Column(Date, nullable=False)
    status = Column(Boolean, nullable=False, default=True)

    # Relacionamento com Estoque
    estoque = relationship("Estoque", back_populates="produto")
    movimentacoes_estoque = relationship(
        "MovimentacaoEstoque", 
        back_populates="produto"
    )
 