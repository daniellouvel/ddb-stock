from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models import Emplacement as EmplacementModel
from app.schemas import EmplacementCreate, EmplacementUpdate, Emplacement

router = APIRouter(prefix="/emplacements", tags=["Emplacements"])

@router.post("/", response_model=Emplacement)
def creer_emplacement(emplacement: EmplacementCreate, db: Session = Depends(get_db)):
    """Créer un nouvel emplacement"""
    
    # Convertir en majuscules
    emplacement.code_emplacement = emplacement.code_emplacement.upper()
    
    # Vérifier unicité du code
    existe = db.query(EmplacementModel).filter(
        EmplacementModel.code_emplacement == emplacement.code_emplacement
    ).first()
    
    if existe:
        raise HTTPException(
            status_code=400,
            detail=f"Code emplacement {emplacement.code_emplacement} déjà utilisé"
        )
    
    # Si parent_id spécifié, vérifier qu'il existe
    if emplacement.parent_id:
        parent = db.query(EmplacementModel).filter(
            EmplacementModel.id == emplacement.parent_id
        ).first()
        if not parent:
            raise HTTPException(status_code=404, detail="Emplacement parent non trouvé")
        
        # Calculer le niveau automatiquement
        emplacement.niveau = parent.niveau + 1
    
    # Créer l'emplacement
    db_emplacement = EmplacementModel(**emplacement.model_dump())
    db.add(db_emplacement)
    db.commit()
    db.refresh(db_emplacement)
    
    return db_emplacement

@router.get("/", response_model=List[Emplacement])
def lire_emplacements(
    skip: int = 0,
    limit: int = 100,
    parent_id: Optional[int] = None,
    niveau: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Lister tous les emplacements avec filtres optionnels"""
    query = db.query(EmplacementModel)
    
    if parent_id is not None:
        if parent_id == 0:
            # Racines (sans parent)
            query = query.filter(EmplacementModel.parent_id.is_(None))
        else:
            # Enfants d'un parent spécifique
            query = query.filter(EmplacementModel.parent_id == parent_id)
    
    if niveau is not None:
        query = query.filter(EmplacementModel.niveau == niveau)
    
    emplacements = query.offset(skip).limit(limit).all()
    return emplacements

@router.get("/{emplacement_id}", response_model=Emplacement)
def lire_emplacement(emplacement_id: int, db: Session = Depends(get_db)):
    """Lire un emplacement spécifique"""
    emplacement = db.query(EmplacementModel).filter(
        EmplacementModel.id == emplacement_id
    ).first()
    
    if not emplacement:
        raise HTTPException(status_code=404, detail="Emplacement non trouvé")
    
    return emplacement

@router.put("/{emplacement_id}", response_model=Emplacement)
def modifier_emplacement(
    emplacement_id: int,
    emplacement_update: EmplacementUpdate,
    db: Session = Depends(get_db)
):
    """Modifier un emplacement"""
    db_emplacement = db.query(EmplacementModel).filter(
        EmplacementModel.id == emplacement_id
    ).first()
    
    if not db_emplacement:
        raise HTTPException(status_code=404, detail="Emplacement non trouvé")
    
    # Mettre à jour les champs fournis
    update_data = emplacement_update.model_dump(exclude_unset=True)
    
    # Si parent_id est modifié, recalculer le niveau
    if "parent_id" in update_data:
        if update_data["parent_id"]:
            parent = db.query(EmplacementModel).filter(
                EmplacementModel.id == update_data["parent_id"]
            ).first()
            if not parent:
                raise HTTPException(status_code=404, detail="Emplacement parent non trouvé")
            update_data["niveau"] = parent.niveau + 1
        else:
            update_data["niveau"] = 1
    
    for key, value in update_data.items():
        setattr(db_emplacement, key, value)
    
    db.commit()
    db.refresh(db_emplacement)
    
    return db_emplacement

@router.delete("/{emplacement_id}")
def supprimer_emplacement(emplacement_id: int, db: Session = Depends(get_db)):
    """Supprimer un emplacement (si aucun article associé)"""
    emplacement = db.query(EmplacementModel).filter(
        EmplacementModel.id == emplacement_id
    ).first()
    
    if not emplacement:
        raise HTTPException(status_code=404, detail="Emplacement non trouvé")
    
    # Vérifier qu'il n'y a pas d'articles
    if emplacement.articles:
        raise HTTPException(
            status_code=400,
            detail=f"Impossible de supprimer : {len(emplacement.articles)} article(s) associé(s)"
        )
    
    # Vérifier qu'il n'y a pas d'emplacements enfants
    enfants = db.query(EmplacementModel).filter(
        EmplacementModel.parent_id == emplacement_id
    ).count()
    
    if enfants > 0:
        raise HTTPException(
            status_code=400,
            detail=f"Impossible de supprimer : {enfants} emplacement(s) enfant(s)"
        )
    
    db.delete(emplacement)
    db.commit()
    
    return {"message": f"Emplacement {emplacement.code_emplacement} supprimé"}

@router.get("/code/{code_emplacement}", response_model=Emplacement)
def chercher_par_code(code_emplacement: str, db: Session = Depends(get_db)):
    """Chercher un emplacement par son code"""
    # Convertir en majuscules pour la recherche
    code_emplacement = code_emplacement.upper()
    
    emplacement = db.query(EmplacementModel).filter(
        EmplacementModel.code_emplacement == code_emplacement
    ).first()
    
    if not emplacement:
        raise HTTPException(
            status_code=404,
            detail=f"Emplacement {code_emplacement} non trouvé"
        )
    
    return emplacement

@router.get("/{emplacement_id}/enfants", response_model=List[Emplacement])
def lire_enfants(emplacement_id: int, db: Session = Depends(get_db)):
    """Lister tous les enfants directs d'un emplacement"""
    # Vérifier que l'emplacement parent existe
    parent = db.query(EmplacementModel).filter(
        EmplacementModel.id == emplacement_id
    ).first()
    
    if not parent:
        raise HTTPException(status_code=404, detail="Emplacement parent non trouvé")
    
    enfants = db.query(EmplacementModel).filter(
        EmplacementModel.parent_id == emplacement_id
    ).all()
    
    return enfants

@router.get("/{emplacement_id}/hierarchie")
def lire_hierarchie(emplacement_id: int, db: Session = Depends(get_db)):
    """Obtenir toute la hiérarchie (parents et enfants) d'un emplacement"""
    emplacement = db.query(EmplacementModel).filter(
        EmplacementModel.id == emplacement_id
    ).first()
    
    if not emplacement:
        raise HTTPException(status_code=404, detail="Emplacement non trouvé")
    
    # Remonter la hiérarchie (parents)
    chemin = []
    current = emplacement
    while current:
        chemin.insert(0, {
            "id": current.id,
            "code_emplacement": current.code_emplacement,
            "nom": current.nom,
            "niveau": current.niveau
        })
        if current.parent_id:
            current = db.query(EmplacementModel).filter(
                EmplacementModel.id == current.parent_id
            ).first()
        else:
            current = None
    
    # Récupérer tous les enfants (récursif)
    def get_enfants_recursif(parent_id):
        enfants = db.query(EmplacementModel).filter(
            EmplacementModel.parent_id == parent_id
        ).all()
        
        result = []
        for enfant in enfants:
            result.append({
                "id": enfant.id,
                "code_emplacement": enfant.code_emplacement,
                "nom": enfant.nom,
                "niveau": enfant.niveau,
                "enfants": get_enfants_recursif(enfant.id)
            })
        return result
    
    enfants = get_enfants_recursif(emplacement_id)
    
    return {
        "chemin": chemin,
        "emplacement": {
            "id": emplacement.id,
            "code_emplacement": emplacement.code_emplacement,
            "nom": emplacement.nom,
            "niveau": emplacement.niveau,
            "description": emplacement.description
        },
        "enfants": enfants
    }