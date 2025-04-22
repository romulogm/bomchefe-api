from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import crud, schemas, models
from app.database import get_db

router = APIRouter()

@router.get("/", response_model=list[schemas.Venda])
def get_vendas(db: Session = Depends(get_db), skip: int = 0, limit: int = 100):
    return crud.get_vendas(db=db, skip=skip, limit=limit)

@router.get("/{venda_id}", response_model=schemas.Venda)
def get_venda(venda_id: int, db: Session = Depends(get_db)):
    return crud.get_venda(db=db, venda_id=venda_id)

@router.post("/", response_model=schemas.Venda)
def create_venda(venda: schemas.VendaCreate, db: Session = Depends(get_db)):
    return crud.create_venda(db=db, venda=venda)

@router.put("/{venda_id}", response_model=schemas.Venda)
def update_venda(venda_id: int, venda: schemas.VendaCreate, db: Session = Depends(get_db)):
    return crud.update_venda(db=db, venda_id=venda_id, venda=venda)

@router.delete("/{venda_id}", response_model=schemas.Venda)
def delete_venda(venda_id: int, db: Session = Depends(get_db)):
    return crud.delete_venda(db=db, venda_id=venda_id)

@router.post("/{venda_id}/itens", response_model=schemas.itens_venda.ItemVendaCreate)
def create_item_venda(venda_id: int, item: schemas.itens_venda.ItemVendaCreate, db: Session = Depends(get_db)):
    venda = db.query(models.Venda).filter(models.Venda.venda_id == venda_id).first()
    if not venda:
        raise HTTPException(status_code=404, detail="Venda não encontrada.")

    subtotal = item.quantidade * item.preco_unitario

    novo_item = models.ItemVenda(
        venda_id=venda_id,
        produto_id=item.produto_id,
        quantidade=item.quantidade,
        preco_unitario=item.preco_unitario,
        subtotal=subtotal
    )

    db.add(novo_item)
    db.commit()
    db.refresh(novo_item)

    # Atualizar valor_total da venda
    venda.valor_total += subtotal
    db.commit()

    return item


@router.put("/{venda_id}/itens/{item_id}")
def update_item_venda(venda_id: int, item_id: int, item_update: schemas.itens_venda.ItemVendaUpdate, db: Session = Depends(get_db)):
    item_venda = db.query(models.ItemVenda).filter(
        models.ItemVenda.item_id == item_id,
        models.ItemVenda.venda_id == venda_id
    ).first()

    if not item_venda:
        raise HTTPException(status_code=404, detail="Item da venda não encontrado.")

    # Atualiza o item
    item_venda.quantidade = item_update.quantidade
    item_venda.preco_unitario = item_update.preco_unitario
    item_venda.subtotal = item_update.quantidade * item_update.preco_unitario
    db.commit()

    # Atualizar valor_total da venda
    venda = db.query(models.Venda).filter(models.Venda.venda_id == venda_id).first()
    itens = db.query(models.ItemVenda).filter(models.ItemVenda.venda_id == venda_id).all()
    venda.valor_total = sum(item.subtotal for item in itens)
    db.commit()

    return {"message": "Item de venda atualizado com sucesso."}


@router.delete("/{venda_id}/itens/{item_id}")
def delete_item_venda(venda_id: int, item_id: int, db: Session = Depends(get_db)):
    item_venda = db.query(models.ItemVenda).filter(
        models.ItemVenda.item_id == item_id,
        models.ItemVenda.venda_id == venda_id
    ).first()

    if not item_venda:
        raise HTTPException(status_code=404, detail="Item da venda não encontrado.")

    subtotal_removido = item_venda.subtotal

    db.delete(item_venda)
    db.commit()

    # Atualizar valor_total da venda
    venda = db.query(models.Venda).filter(models.Venda.venda_id == venda_id).first()
    if venda:
        venda.valor_total -= subtotal_removido
        if venda.valor_total < 0:
            venda.valor_total = 0
        db.commit()

    return {"message": "Item de venda removido com sucesso."}