from sqlalchemy import Column, Integer, ForeignKey, String, Date, DateTime, Boolean
from sqlalchemy.orm import relationship
from app.database import Base 

class Estoque(Base):
    __tablename__ = "estoque"
    
    feira_id = Column(Integer, ForeignKey("feiras.feira_id"), nullable=True)
    estoque_id = Column(Integer, primary_key=True, index=True)
    produto_id = Column(Integer, ForeignKey("produtos.produto_id"), nullable=False)
    quantidade = Column(Integer, nullable=False) # Quantidade ATUAL deste item em estoque
    lote = Column(String(50))
    data_producao = Column(Date)
    data_validade = Column(Date)
    localizacao = Column(String(50))
    data_atualizacao = Column(DateTime, nullable=False)
    venda_consolidada = Column(Boolean, default=False, nullable=False, index=True)
    
    movimentacoes_estoque = relationship("MovimentacaoEstoque", back_populates="estoque")
    produto = relationship("Produto", back_populates="estoque")
    feira = relationship("Feira", back_populates="itens_de_estoque")
    vendas_associadas_a_este_estoque = relationship("ItemVenda", back_populates="item_de_estoque_utilizado")