from sqlalchemy import Column, Integer, String, Date, ForeignKey, TIMESTAMP, func
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
    data_atualizacao = Column(TIMESTAMP, server_default=func.now(), nullable=False)
