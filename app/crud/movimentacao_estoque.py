from sqlalchemy.orm import Session
from .. import models, schemas, crud
from datetime import datetime
from app.schemas import EstoqueCreate, MovimentacaoEstoqueCreate
# Para este exemplo, vamos assumir que models e schemas são acessíveis
from ..models import MovimentacaoEstoque as MovimentacaoEstoqueModel # Alias para evitar conflito
# from ..schemas import MovimentacaoEstoqueCreate # Usaremos o schema definido acima

def create_movimentacao_estoque(db: Session, movimentacao: MovimentacaoEstoqueCreate) -> MovimentacaoEstoqueModel:
    """Cria um novo registro de movimentação de estoque."""
    db_movimentacao_data = movimentacao.model_dump()
    
    # Garante que data_movimentacao tenha um valor se não foi fornecido
    if db_movimentacao_data.get('data_movimentacao') is None:
        db_movimentacao_data['data_movimentacao'] = datetime.utcnow()

    db_movimentacao = MovimentacaoEstoqueModel(**db_movimentacao_data)
    db.add(db_movimentacao)
    # O commit geralmente é feito na função que chama esta, ou no final do endpoint.
    return db_movimentacao