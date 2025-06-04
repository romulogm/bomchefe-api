from sqlalchemy import Column, Integer, ForeignKey, String, Date, DateTime, Text
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime

class MovimentacaoEstoque(Base):
    __tablename__ = "movimentacoes_estoque"

    movimentacao_id = Column(Integer, primary_key=True, index=True)
    data_movimentacao = Column(DateTime, nullable=False, default=datetime.utcnow)
    produto_id = Column(Integer, ForeignKey("produtos.produto_id"), nullable=False)
    estoque_id = Column(Integer, ForeignKey("estoque.estoque_id"), nullable=False) 
    quantidade_alterada = Column(Integer, nullable=False) # Positive for increase, Negative for decrease
    tipo_movimentacao = Column(String(50), nullable=False) 
    # e.g., 'ENTRADA_PRODUCAO', 'SAIDA_PARA_FEIRA', 'ENTRADA_EM_FEIRA', 
    # 'VENDA_EM_FEIRA', 'RETORNO_DE_FEIRA_SAIDA', 'RETORNO_DE_FEIRA_ENTRADA', 'AJUSTE_ESTOQUE'
    feira_id = Column(Integer, ForeignKey("feiras.feira_id"), nullable=True) # If related to a fair operation
    venda_id = Column(Integer, ForeignKey("vendas.venda_id"), nullable=True) # If related to a sale depletion
    item_venda_id = Column(Integer, ForeignKey("itens_venda.item_venda_id"), nullable=True) # If related to a specific sale item
    observacao = Column(Text, nullable=True)

    produto = relationship("Produto", back_populates="movimentacoes_estoque")
    estoque = relationship("Estoque", back_populates="movimentacoes_estoque")
    feira = relationship("Feira", back_populates="movimentacoes_estoque")
    # venda_associada = relationship("Venda", back_populates="movimentacoes_estoque")
    # item_venda_associado = relationship("ItemVenda", back_populates="movimentacoes_associadas")
