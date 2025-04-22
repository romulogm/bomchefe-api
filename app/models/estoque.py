from sqlalchemy import Column, Integer, ForeignKey, String, Date, DateTime
from sqlalchemy.orm import relationship
from app.database import Base

class Estoque(Base):
    __tablename__ = "estoque"

    estoque_id = Column(Integer, primary_key=True, index=True)
    produto_id = Column(Integer, ForeignKey("produtos.produto_id"), nullable=False)
    quantidade = Column(Integer, nullable=False)
    lote = Column(String(50))
    data_producao = Column(Date)
    data_validade = Column(Date)
    localizacao = Column(String(50))
    data_atualizacao = Column(DateTime, nullable=False)

    # Relacionamento com Produto
    produto = relationship("Produto", back_populates="estoque")
