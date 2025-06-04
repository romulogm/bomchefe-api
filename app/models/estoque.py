from sqlalchemy import Column, Integer, ForeignKey, String, Date, DateTime
from sqlalchemy.orm import relationship
from app.database import Base # Sua Base declarativa do SQLAlchemy
# Certifique-se de que ItemVenda seja importável aqui se estiver em outro arquivo.
# from .item_venda import ItemVenda # Exemplo de importação

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

    # Relacionamentos existentes
    movimentacoes_estoque = relationship("MovimentacaoEstoque", back_populates="estoque")
    produto = relationship("Produto", back_populates="estoque")
    feira = relationship("Feira", back_populates="itens_de_estoque")

    # Novo relacionamento: liga esta entrada de estoque aos itens de venda que a utilizaram.
    # Uma entrada de estoque pode ser usada em múltiplos itens de venda (parcialmente ou totalmente).
    vendas_associadas_a_este_estoque = relationship("ItemVenda", back_populates="item_de_estoque_utilizado")