from sqlalchemy import Column, Integer, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from app.database import Base

class ItemVenda(Base):
    __tablename__ = "itens_venda"

    item_id = Column(Integer, primary_key=True, index=True)
    venda_id = Column(Integer, ForeignKey("vendas.venda_id"), nullable=False)
    produto_id = Column(Integer, ForeignKey("produtos.produto_id"), nullable=False)
    quantidade = Column(Integer, nullable=False)
    preco_unitario = Column(Numeric(10, 2), nullable=False)
    subtotal = Column(Numeric(10, 2), nullable=False)

    venda = relationship("Venda", back_populates="itens_venda")
    produto = relationship("Produto")
