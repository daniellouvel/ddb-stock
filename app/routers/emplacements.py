from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app import models, schemas
from app.database import get_db

router = APIRouter(prefix="/emplacements", tags=["Emplacements"])

@router.post("/", response_model=schemas.Emplacement, status_code=201)
def create_emplacement(emplacement: schemas.EmplacementCreate, db: Session = Depends(get_db)):
    """Créer un nouvel emplacement"""
    # Vérifier si code_emplacement existe déjà
    db_emplacement = db.query(models.Emplacement).filter(
        models.Emplacement.code_emplacement == emplacement.code_emplacement
    ).first()
    if db_emplacement:
        raise HTTPException(status_code=400, detail="Code emplacement déjà existant")
    
    # Vérifier que parent_id existe si fourni
    if emplacement.parent_id:
        parent = db.query(models.Emplacement).filter(
            models.Emplacement.id == emplacement.parent_id
        ).first()
        if not parent:
            raise HTTPException(status_code=404, detail="Emplacement parent non trouvé")
    
    db_emplacement = models.Emplacement(**emplacement.model_dump())
    db.add(db_emplacement)
    db.commit()
    db.refresh(db_emplacement)
    return db_emplacement

@router.get("/", response_model=List[schemas.Emplacement])
def read_emplacements(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Récupérer la liste des emplacements"""
    emplacements = db.query(models.Emplacement).offset(skip).limit(limit).all()
    return emplacements

@router.get("/{emplacement_id}", response_model=schemas.Emplacement)
def read_emplacement(emplacement_id: int, db: Session = Depends(get_db)):
    """Récupérer un emplacement par ID"""
    emplacement = db.query(models.Emplacement).filter(
        models.Emplacement.id == emplacement_id
    ).first()
    if emplacement is None:
        raise HTTPException(status_code=404, detail="Emplacement non trouvé")
    return emplacement

@router.get("/code/{code_emplacement}", response_model=schemas.Emplacement)
def read_emplacement_by_code(code_emplacement: str, db: Session = Depends(get_db)):
    """Récupérer un emplacement par code (EMP###)"""
    emplacement = db.query(models.Emplacement).filter(
        models.Emplacement.code_emplacement == code_emplacement
    ).first()
    if emplacement is None:
        raise HTTPException(status_code=404, detail="Emplacement non trouvé")
    return emplacement

@router.get("/niveau/{niveau}", response_model=List[schemas.Emplacement])
def read_emplacements_by_niveau(niveau: int, db: Session = Depends(get_db)):
    """Récupérer tous les emplacements d'un niveau hiérarchique"""
    emplacements = db.query(models.Emplacement).filter(
        models.Emplacement.niveau == niveau
    ).all()
    return emplacements

@router.get("/{parent_id}/enfants", response_model=List[schemas.Emplacement])
def read_emplacements_enfants(parent_id: int, db: Session = Depends(get_db)):
    """Récupérer tous les emplacements enfants d'un emplacement parent"""
    emplacements = db.query(models.Emplacement).filter(
        models.Emplacement.parent_id == parent_id
    ).all()
    return emplacements

@router.put("/{emplacement_id}", response_model=schemas.Emplacement)
def update_emplacement(
    emplacement_id: int, 
    emplacement: schemas.EmplacementUpdate, 
    db: Session = Depends(get_db)
):
    """Mettre à jour un emplacement"""
    db_emplacement = db.query(models.Emplacement).filter(
        models.Emplacement.id == emplacement_id
    ).first()
    if db_emplacement is None:
        raise HTTPException(status_code=404, detail="Emplacement non trouvé")
    
    # Vérifier que parent_id existe si modifié
    if emplacement.parent_id and emplacement.parent_id != db_emplacement.parent_id:
        parent = db.query(models.Emplacement).filter(
            models.Emplacement.id == emplacement.parent_id
        ).first()
        if not parent:
            raise HTTPException(status_code=404, detail="Emplacement parent non trouvé")
    
    for key, value in emplacement.model_dump(exclude_unset=True).items():
        setattr(db_emplacement, key, value)
    
    db.commit()
    db.refresh(db_emplacement)
    return db_emplacement

@router.delete("/{emplacement_id}", status_code=204)
def delete_emplacement(emplacement_id: int, db: Session = Depends(get_db)):
    """Supprimer un emplacement"""
    db_emplacement = db.query(models.Emplacement).filter(
        models.Emplacement.id == emplacement_id
    ).first()
    if db_emplacement is None:
        raise HTTPException(status_code=404, detail="Emplacement non trouvé")
    
    # Vérifier qu'il n'y a pas d'articles dans cet emplacement
    articles_count = db.query(models.Article).filter(
        models.Article.emplacement_id == emplacement_id
    ).count()
    if articles_count > 0:
        raise HTTPException(
            status_code=400, 
            detail=f"Impossible de supprimer : {articles_count} article(s) dans cet emplacement"
        )
    
    # Vérifier qu'il n'y a pas d'emplacements enfants
    enfants_count = db.query(models.Emplacement).filter(
        models.Emplacement.parent_id == emplacement_id
    ).count()
    if enfants_count > 0:
        raise HTTPException(
            status_code=400,
            detail=f"Impossible de supprimer : {enfants_count} emplacement(s) enfant(s)"
        )
    
    db.delete(db_emplacement)
    db.commit()
    return None
