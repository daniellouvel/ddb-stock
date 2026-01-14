from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app import models, schemas
from app.database import get_db

router = APIRouter(prefix="/articles", tags=["Articles"])

@router.post("/", response_model=schemas.Article, status_code=201)
def create_article(article: schemas.ArticleCreate, db: Session = Depends(get_db)):
    """Créer un nouvel article"""
    # Vérifier si code_article existe déjà
    db_article = db.query(models.Article).filter(
        models.Article.code_article == article.code_article
    ).first()
    if db_article:
        raise HTTPException(status_code=400, detail="Code article déjà existant")
    
    # Vérifier que le produit existe
    produit = db.query(models.Produit).filter(
        models.Produit.id == article.produit_id
    ).first()
    if not produit:
        raise HTTPException(status_code=404, detail="Produit non trouvé")
    
    # Vérifier que l'emplacement existe
    emplacement = db.query(models.Emplacement).filter(
        models.Emplacement.id == article.emplacement_id
    ).first()
    if not emplacement:
        raise HTTPException(status_code=404, detail="Emplacement non trouvé")
    
    db_article = models.Article(**article.model_dump())
    db.add(db_article)
    db.commit()
    db.refresh(db_article)
    return db_article

@router.get("/", response_model=List[schemas.Article])
def read_articles(
    skip: int = 0, 
    limit: int = 100, 
    emplacement_id: Optional[int] = None,
    produit_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Récupérer la liste des articles avec filtres optionnels"""
    query = db.query(models.Article)
    
    if emplacement_id:
        query = query.filter(models.Article.emplacement_id == emplacement_id)
    
    if produit_id:
        query = query.filter(models.Article.produit_id == produit_id)
    
    articles = query.offset(skip).limit(limit).all()
    return articles

@router.get("/{article_id}", response_model=schemas.Article)
def read_article(article_id: int, db: Session = Depends(get_db)):
    """Récupérer un article par ID"""
    article = db.query(models.Article).filter(
        models.Article.id == article_id
    ).first()
    if article is None:
        raise HTTPException(status_code=404, detail="Article non trouvé")
    return article

@router.get("/code/{code_article}", response_model=schemas.Article)
def read_article_by_code(code_article: str, db: Session = Depends(get_db)):
    """Récupérer un article par code (GG####)"""
    article = db.query(models.Article).filter(
        models.Article.code_article == code_article
    ).first()
    if article is None:
        raise HTTPException(status_code=404, detail="Article non trouvé")
    return article

@router.get("/peremption/prochaines", response_model=List[schemas.Article])
def read_articles_peremption_proche(jours: int = 30, db: Session = Depends(get_db)):
    """Récupérer les articles qui périment dans X jours"""
    date_limite = datetime.now()
    from datetime import timedelta
    date_future = date_limite + timedelta(days=jours)
    
    articles = db.query(models.Article).filter(
        models.Article.date_peremption.isnot(None),
        models.Article.date_peremption <= date_future,
        models.Article.date_peremption >= date_limite
    ).all()
    return articles

@router.get("/peremption/expirees", response_model=List[schemas.Article])
def read_articles_expires(db: Session = Depends(get_db)):
    """Récupérer les articles déjà périmés"""
    date_actuelle = datetime.now()
    
    articles = db.query(models.Article).filter(
        models.Article.date_peremption.isnot(None),
        models.Article.date_peremption < date_actuelle
    ).all()
    return articles

@router.put("/{article_id}", response_model=schemas.Article)
def update_article(
    article_id: int, 
    article: schemas.ArticleUpdate, 
    db: Session = Depends(get_db)
):
    """Mettre à jour un article"""
    db_article = db.query(models.Article).filter(
        models.Article.id == article_id
    ).first()
    if db_article is None:
        raise HTTPException(status_code=404, detail="Article non trouvé")
    
    # Vérifier que le produit existe si modifié
    if article.produit_id and article.produit_id != db_article.produit_id:
        produit = db.query(models.Produit).filter(
            models.Produit.id == article.produit_id
        ).first()
        if not produit:
            raise HTTPException(status_code=404, detail="Produit non trouvé")
    
    # Vérifier que l'emplacement existe si modifié
    if article.emplacement_id and article.emplacement_id != db_article.emplacement_id:
        emplacement = db.query(models.Emplacement).filter(
            models.Emplacement.id == article.emplacement_id
        ).first()
        if not emplacement:
            raise HTTPException(status_code=404, detail="Emplacement non trouvé")
    
    for key, value in article.model_dump(exclude_unset=True).items():
        setattr(db_article, key, value)
    
    db.commit()
    db.refresh(db_article)
    return db_article

@router.delete("/{article_id}", status_code=204)
def delete_article(article_id: int, db: Session = Depends(get_db)):
    """Supprimer un article"""
    db_article = db.query(models.Article).filter(
        models.Article.id == article_id
    ).first()
    if db_article is None:
        raise HTTPException(status_code=404, detail="Article non trouvé")
    
    db.delete(db_article)
    db.commit()
    return None

@router.patch("/{article_id}/quantite", response_model=schemas.Article)
def update_article_quantite(
    article_id: int, 
    quantite: int,
    db: Session = Depends(get_db)
):
    """Mettre à jour uniquement la quantité d'un article"""
    if quantite < 0:
        raise HTTPException(status_code=400, detail="La quantité ne peut pas être négative")
    
    db_article = db.query(models.Article).filter(
        models.Article.id == article_id
    ).first()
    if db_article is None:
        raise HTTPException(status_code=404, detail="Article non trouvé")
    
    db_article.quantite = quantite
    db.commit()
    db.refresh(db_article)
    return db_article
