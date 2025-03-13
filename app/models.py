from sqlalchemy import Column, Integer, String, Text, Date, ForeignKey, DECIMAL, DateTime, CheckConstraint, func
from sqlalchemy.orm import relationship
from .database import Base 

class Produto(Base):
    __tablename__ = "produtos"

    id_produto = Column(Integer, primary_key=True)
    nome = Column(String(255), nullable=False)
    descricao = Column(Text, nullable=True)
    preco = Column(DECIMAL(10,2), nullable=False)
    estoque_atual = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        CheckConstraint('preco >= 0', name='check_preco_positivo'),
        CheckConstraint('estoque_atual >= 0', name='check_estoque_positivo'),
    )

#     ingredientes = relationship("ProdutoIngrediente", back_populates="produto")
#     estoque = relationship("EstoqueProduto", back_populates="produto")
#     vendas = relationship("VendaProduto", back_populates="produto")

# class Ingrediente(Base):
#     __tablename__ = "ingredientes"

#     id_ingrediente = Column(Integer, primary_key=True)
#     nome = Column(String(255), nullable=False)
#     created_at = Column(DateTime, server_default=func.now())
#     updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

#     produtos = relationship("ProdutoIngrediente", back_populates="ingrediente")
#     estoque = relationship("EstoqueIngrediente", back_populates="ingrediente")
#     compras = relationship("CompraIngrediente", back_populates="ingrediente")

# class ProdutoIngrediente(Base):
#     __tablename__ = "produtos_ingredientes"

#     id_produto = Column(Integer, ForeignKey("produtos.id_produto"), primary_key=True)
#     id_ingrediente = Column(Integer, ForeignKey("ingredientes.id_ingrediente"), primary_key=True)
#     quantidade = Column(DECIMAL(10,2), nullable=False)
#     created_at = Column(DateTime, server_default=func.now())
#     updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

#     __table_args__ = (
#         CheckConstraint('quantidade > 0', name='check_quantidade_positiva'),
#     )

#     produto = relationship("Produto", back_populates="ingredientes")
#     ingrediente = relationship("Ingrediente", back_populates="produtos")

# class EstoqueProduto(Base):
#     __tablename__ = "estoque_produtos"

#     id_estoque_produto = Column(Integer, primary_key=True)
#     id_produto = Column(Integer, ForeignKey("produtos.id_produto"))
#     quantidade = Column(Integer, nullable=False)
#     data_atualizacao = Column(Date, nullable=False)
#     created_at = Column(DateTime, server_default=func.now())
#     updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

#     __table_args__ = (
#         CheckConstraint('quantidade >= 0', name='check_quantidade_positiva'),
#     )

#     produto = relationship("Produto", back_populates="estoque")

# class EstoqueIngrediente(Base):
#     __tablename__ = "estoque_ingredientes"

#     id_estoque_ingrediente = Column(Integer, primary_key=True)
#     id_ingrediente = Column(Integer, ForeignKey("ingredientes.id_ingrediente"))
#     quantidade = Column(Integer, nullable=False)
#     data_atualizacao = Column(Date, nullable=False)
#     created_at = Column(DateTime, server_default=func.now())
#     updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

#     __table_args__ = (
#         CheckConstraint('quantidade >= 0', name='check_quantidade_positiva'),
#     )

#     ingrediente = relationship("Ingrediente", back_populates="estoque")

# class CompraIngrediente(Base):
#     __tablename__ = "compras_ingredientes"

#     id_compra_ingrediente = Column(Integer, primary_key=True)
#     id_ingrediente = Column(Integer, ForeignKey("ingredientes.id_ingrediente"))
#     quantidade = Column(Integer, nullable=False)
#     preco_unitario = Column(DECIMAL(10,2), nullable=False)
#     data_compra = Column(Date, nullable=False)
#     created_at = Column(DateTime, server_default=func.now())
#     updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

#     __table_args__ = (
#         CheckConstraint('quantidade > 0', name='check_quantidade_positiva'),
#         CheckConstraint('preco_unitario >= 0', name='check_preco_positivo'),
#     )

#     ingrediente = relationship("Ingrediente", back_populates="compras")

# class Cliente(Base):
#     __tablename__ = "clientes"

#     id_cliente = Column(Integer, primary_key=True)
#     nome = Column(String(255), nullable=False)
#     telefone = Column(String(20), nullable=True)
#     email = Column(String(255), nullable=True)
#     endereco = Column(Text, nullable=True)
#     created_at = Column(DateTime, server_default=func.now())
#     updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

#     vendas = relationship("Venda", back_populates="cliente")

# class Venda(Base):
#     __tablename__ = "vendas"

#     id_venda = Column(Integer, primary_key=True)
#     id_cliente = Column(Integer, ForeignKey("clientes.id_cliente"))
#     data_venda = Column(Date, nullable=False, server_default=func.current_date())
#     total_venda = Column(DECIMAL(10,2), nullable=False)
#     created_at = Column(DateTime, server_default=func.now())
#     updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

#     __table_args__ = (
#         CheckConstraint('total_venda >= 0', name='check_total_venda_positivo'),
#     )

#     cliente = relationship("Cliente", back_populates="vendas")
#     produtos = relationship("VendaProduto", back_populates="venda")

# class VendaProduto(Base):
#     __tablename__ = "vendas_produtos"

#     id_venda = Column(Integer, ForeignKey("vendas.id_venda"), primary_key=True)
#     id_produto = Column(Integer, ForeignKey("produtos.id_produto"), primary_key=True)
#     quantidade = Column(Integer, nullable=False)
#     preco_unitario = Column(DECIMAL(10,2), nullable=False)
#     created_at = Column(DateTime, server_default=func.now())
#     updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

#     __table_args__ = (
#         CheckConstraint('quantidade > 0', name='check_quantidade_positiva'),
#         CheckConstraint('preco_unitario >= 0', name='check_preco_positivo'),
#     )

#     venda = relationship("Venda", back_populates="produtos")
#     produto = relationship("Produto", back_populates="vendas")