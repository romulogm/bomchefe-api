from sqlalchemy import Column, Integer, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from app.database import Base 

class ItemVenda(Base):
    __tablename__ = "itens_venda"

    item_venda_id = Column(Integer, primary_key=True, index=True)
    venda_id = Column(Integer, ForeignKey("vendas.venda_id"), nullable=False)
    estoque_id = Column(Integer, ForeignKey("estoque.estoque_id"), nullable=False)
    quantidade = Column(Integer, nullable=False)
    preco_unitario = Column(Numeric(10, 2), nullable=False)
    # Relacionamento de volta para Venda (já definido no seu modelo Venda)
    venda = relationship("Venda", back_populates="itens_venda")

    # Relacionamento com Estoque: cada item de venda vem de um item de estoque.
    # "item_de_estoque_utilizado" será o atributo em ItemVenda para acessar o Estoque.
    # "vendas_associadas_a_este_estoque" será o atributo em Estoque para acessar os ItensVenda.
    item_de_estoque_utilizado = relationship("Estoque", back_populates="vendas_associadas_a_este_estoque")
    # produto_id = Column(Integer, ForeignKey("produtos.produto_id"), nullable=False)
    # produto = relationship("Produto")