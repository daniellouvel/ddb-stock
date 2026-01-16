from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import Produit as ProduitModel
from app.schemas import ProduitCreate, ProduitUpdate, Produit

router = APIRouter(prefix="/produits", tags=["Produits"])

@router.post("/", response_model=Produit)
def creer_produit(produit: ProduitCreate, db: Session = Depends(get_db)):
    """Créer un nouveau produit"""
    
    # Vérifier unicité de l'EAN si fourni
    if produit.ean:
        existe = db.query(ProduitModel).filter(ProduitModel.ean == produit.ean).first()
        if existe:
            raise HTTPException(status_code=400, detail=f"EAN {produit.ean} déjà utilisé")
    
    # Créer le produit
    db_produit = ProduitModel(**produit.model_dump())
    db.add(db_produit)
    db.commit()
    db.refresh(db_produit)
    
    return db_produit

@router.get("/", response_model=List[Produit])
def lire_produits(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Lister tous les produits"""
    produits = db.query(ProduitModel).offset(skip).limit(limit).all()
    return produits

@router.get("/{produit_id}", response_model=Produit)
def lire_produit(produit_id: int, db: Session = Depends(get_db)):
    """Lire un produit spécifique"""
    produit = db.query(ProduitModel).filter(ProduitModel.id == produit_id).first()
    if not produit:
        raise HTTPException(status_code=404, detail="Produit non trouvé")
    return produit

@router.put("/{produit_id}", response_model=Produit)
def modifier_produit(produit_id: int, produit_update: ProduitUpdate, db: Session = Depends(get_db)):
    """Modifier un produit"""
    db_produit = db.query(ProduitModel).filter(ProduitModel.id == produit_id).first()
    if not db_produit:
        raise HTTPException(status_code=404, detail="Produit non trouvé")
    
    # Vérifier unicité EAN si modifié
    if produit_update.ean and produit_update.ean != db_produit.ean:
        existe = db.query(ProduitModel).filter(ProduitModel.ean == produit_update.ean).first()
        if existe:
            raise HTTPException(status_code=400, detail=f"EAN {produit_update.ean} déjà utilisé")
    
    # Mettre à jour
    update_data = produit_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_produit, key, value)
    
    db.commit()
    db.refresh(db_produit)
    return db_produit

@router.delete("/{produit_id}")
def supprimer_produit(produit_id: int, db: Session = Depends(get_db)):
    """Supprimer un produit (si aucun article associé)"""
    produit = db.query(ProduitModel).filter(ProduitModel.id == produit_id).first()
    if not produit:
        raise HTTPException(status_code=404, detail="Produit non trouvé")
    
    # Vérifier qu'il n'y a pas d'articles
    if produit.articles:
        raise HTTPException(
            status_code=400,
            detail=f"Impossible de supprimer : {len(produit.articles)} article(s) associé(s)"
        )
    
    db.delete(produit)
    db.commit()
    return {"message": f"Produit {produit.nom} supprimé"}
