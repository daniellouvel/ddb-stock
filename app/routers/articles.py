from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from app.database import get_db
from app.models import Article, Produit, Emplacement
from app.schemas import ArticleCreate, ArticleResponse, ArticleDetail

router = APIRouter(prefix="/articles", tags=["Articles"])

@router.post("/", response_model=ArticleResponse)
def creer_article(article: ArticleCreate, db: Session = Depends(get_db)):
    """Créer un nouvel article"""
    
    # Vérifier que le produit existe
    produit = db.query(Produit).filter(Produit.id == article.produit_id).first()
    if not produit:
        raise HTTPException(status_code=404, detail="Produit non trouvé")
    
    # Vérifier que l'emplacement existe
    emplacement = db.query(Emplacement).filter(Emplacement.id == article.emplacement_id).first()
    if not emplacement:
        raise HTTPException(status_code=404, detail="Emplacement non trouvé")
    
    # Vérifier que le code_article n'existe pas déjà
    existe = db.query(Article).filter(Article.code_article == article.code_article).first()
    if existe:
        raise HTTPException(status_code=400, detail=f"Code article {article.code_article} déjà utilisé")
    
    # Créer l'article
    db_article = Article(**article.model_dump())
    db.add(db_article)
    db.commit()
    db.refresh(db_article)
    
    return db_article

@router.get("/", response_model=List[ArticleDetail])
def lire_articles(
    skip: int = 0,
    limit: int = 100,
    produit_id: Optional[int] = None,
    emplacement_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Lister tous les articles avec filtres optionnels"""
    query = db.query(Article)
    
    if produit_id:
        query = query.filter(Article.produit_id == produit_id)
    if emplacement_id:
        query = query.filter(Article.emplacement_id == emplacement_id)
    
    articles = query.offset(skip).limit(limit).all()
    
    # Enrichir avec les données produit et emplacement
    result = []
    for article in articles:
        article_dict = {
            "id": article.id,
            "code_article": article.code_article,
            "produit_id": article.produit_id,
            "emplacement_id": article.emplacement_id,
            "quantite": article.quantite,
            "date_peremption": article.date_peremption,
            "created_at": article.created_at,
            "commentaire": article.commentaire,
            "produit": article.produit,
            "emplacement": article.emplacement
        }
        result.append(article_dict)
    
    return result

@router.get("/{article_id}", response_model=ArticleDetail)
def lire_article(article_id: int, db: Session = Depends(get_db)):
    """Lire un article spécifique"""
    article = db.query(Article).filter(Article.id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article non trouvé")
    
    return {
        "id": article.id,
        "code_article": article.code_article,
        "produit_id": article.produit_id,
        "emplacement_id": article.emplacement_id,
        "quantite": article.quantite,
        "date_peremption": article.date_peremption,
        "created_at": article.created_at,
        "commentaire": article.commentaire,
        "produit": article.produit,
        "emplacement": article.emplacement
    }

@router.put("/{article_id}", response_model=ArticleResponse)
def modifier_article(article_id: int, quantite: int, db: Session = Depends(get_db)):
    """Modifier la quantité d'un article"""
    article = db.query(Article).filter(Article.id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article non trouvé")
    
    if quantite < 0:
        raise HTTPException(status_code=400, detail="La quantité ne peut pas être négative")
    
    article.quantite = quantite
    db.commit()
    db.refresh(article)
    
    return article

@router.delete("/{article_id}")
def supprimer_article(article_id: int, quantite_a_retirer: int = None, db: Session = Depends(get_db)):
    """
    Supprimer ou décrémenter un article
    - Si quantite_a_retirer non fourni ou >= quantité totale : suppression définitive
    - Sinon : décrémente la quantité
    """
    article = db.query(Article).filter(Article.id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article non trouvé")
    
    code_article = article.code_article
    quantite_actuelle = article.quantite
    
    # Si pas de quantité spécifiée ou quantité >= total : suppression complète
    if quantite_a_retirer is None or quantite_a_retirer >= quantite_actuelle:
        db.delete(article)
        db.commit()
        return {
            "action": "suppression_complete",
            "message": f"Article {code_article} supprimé définitivement",
            "code_libere": code_article,
            "quantite_retiree": quantite_actuelle
        }
    
    # Sinon : décrémenter
    if quantite_a_retirer <= 0:
        raise HTTPException(status_code=400, detail="La quantité à retirer doit être positive")
    
    article.quantite -= quantite_a_retirer
    db.commit()
    db.refresh(article)
    
    return {
        "action": "decrementation",
        "message": f"{quantite_a_retirer} article(s) retiré(s) du stock",
        "code_article": code_article,
        "quantite_restante": article.quantite,
        "quantite_retiree": quantite_a_retirer
    }

@router.get("/peremption/prochaines")
def articles_peremption_prochaine(jours: int = 30, db: Session = Depends(get_db)):
    """Articles dont la péremption approche"""
    date_limite = datetime.utcnow() + timedelta(days=jours)
    
    articles = db.query(Article).filter(
        Article.date_peremption.isnot(None),
        Article.date_peremption <= date_limite,
        Article.date_peremption >= datetime.utcnow()
    ).all()
    
    result = []
    for article in articles:
        jours_restants = (article.date_peremption - datetime.utcnow()).days
        article_dict = {
            "id": article.id,
            "code_article": article.code_article,
            "produit_id": article.produit_id,
            "emplacement_id": article.emplacement_id,
            "quantite": article.quantite,
            "date_peremption": article.date_peremption,
            "created_at": article.created_at,
            "commentaire": article.commentaire,
            "produit": article.produit,
            "emplacement": article.emplacement,
            "jours_restants": jours_restants
        }
        result.append(article_dict)
    
    return result

@router.get("/peremption/expirees")
def articles_expires(db: Session = Depends(get_db)):
    """Articles expirés"""
    articles = db.query(Article).filter(
        Article.date_peremption.isnot(None),
        Article.date_peremption < datetime.utcnow()
    ).all()
    
    result = []
    for article in articles:
        jours_expires = (datetime.utcnow() - article.date_peremption).days
        article_dict = {
            "id": article.id,
            "code_article": article.code_article,
            "produit_id": article.produit_id,
            "emplacement_id": article.emplacement_id,
            "quantite": article.quantite,
            "date_peremption": article.date_peremption,
            "created_at": article.created_at,
            "commentaire": article.commentaire,
            "produit": article.produit,
            "emplacement": article.emplacement,
            "jours_expires": jours_expires
        }
        result.append(article_dict)
    
    return result

@router.get("/code/{code_article}", response_model=ArticleDetail)
def chercher_par_code(code_article: str, db: Session = Depends(get_db)):
    """Chercher un article par son code"""
    article = db.query(Article).filter(Article.code_article == code_article.upper()).first()
    if not article:
        raise HTTPException(status_code=404, detail=f"Article {code_article} non trouvé")
    
    return {
        "id": article.id,
        "code_article": article.code_article,
        "produit_id": article.produit_id,
        "emplacement_id": article.emplacement_id,
        "quantite": article.quantite,
        "date_peremption": article.date_peremption,
        "created_at": article.created_at,
        "commentaire": article.commentaire,
        "produit": article.produit,
        "emplacement": article.emplacement
    }
