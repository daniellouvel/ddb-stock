from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app import models, schemas
from app.database import get_db

router = APIRouter(prefix="/produits", tags=["Produits"])

@router.post("/", response_model=schemas.Produit, status_code=201)
def create_produit(produit: schemas.ProduitCreate, db: Session = Depends(get_db)):
    """Créer un nouveau produit"""
    # Vérifier si EAN existe déjà
    if produit.ean:
        db_produit = db.query(models.Produit).filter(models.Produit.ean == produit.ean).first()
        if db_produit:
            raise HTTPException(status_code=400, detail="EAN déjà existant")
    
    db_produit = models.Produit(**produit.model_dump())
    db.add(db_produit)
    db.commit()
    db.refresh(db_produit)
    return db_produit

@router.get("/", response_model=List[schemas.Produit])
def read_produits(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Récupérer la liste des produits"""
    produits = db.query(models.Produit).offset(skip).limit(limit).all()
    return produits

@router.get("/{produit_id}", response_model=schemas.Produit)
def read_produit(produit_id: int, db: Session = Depends(get_db)):
    """Récupérer un produit par ID"""
    produit = db.query(models.Produit).filter(models.Produit.id == produit_id).first()
    if produit is None:
        raise HTTPException(status_code=404, detail="Produit non trouvé")
    return produit

@router.put("/{produit_id}", response_model=schemas.Produit)
def update_produit(produit_id: int, produit: schemas.ProduitUpdate, db: Session = Depends(get_db)):
    """Mettre à jour un produit"""
    db_produit = db.query(models.Produit).filter(models.Produit.id == produit_id).first()
    if db_produit is None:
        raise HTTPException(status_code=404, detail="Produit non trouvé")
    
    for key, value in produit.model_dump(exclude_unset=True).items():
        setattr(db_produit, key, value)
    
    db.commit()
    db.refresh(db_produit)
    return db_produit

@router.delete("/{produit_id}", status_code=204)
def delete_produit(produit_id: int, db: Session = Depends(get_db)):
    """Supprimer un produit"""
    db_produit = db.query(models.Produit).filter(models.Produit.id == produit_id).first()
    if db_produit is None:
        raise HTTPException(status_code=404, detail="Produit non trouvé")
    
    db.delete(db_produit)
    db.commit()
    return None
