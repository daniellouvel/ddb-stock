from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, event
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime

class Produit(Base):
    __tablename__ = "produits"
    
    id = Column(Integer, primary_key=True, index=True)
    ean = Column(String, unique=True, nullable=True, index=True)
    nom = Column(String, nullable=False)
    marque = Column(String, nullable=True)
    description = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow, nullable=True)
    
    articles = relationship("Article", back_populates="produit")

class Emplacement(Base):
    __tablename__ = "emplacements"
    
    id = Column(Integer, primary_key=True, index=True)
    code_emplacement = Column(String, unique=True, nullable=False, index=True)
    nom = Column(String, nullable=False)
    parent_id = Column(Integer, ForeignKey("emplacements.id"), nullable=True)
    niveau = Column(Integer, default=1)
    description = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow, nullable=True)
    
    parent = relationship("Emplacement", remote_side=[id], backref="enfants")
    articles = relationship("Article", back_populates="emplacement")

# Event listener pour convertir code_emplacement en majuscules
@event.listens_for(Emplacement, 'before_insert')
@event.listens_for(Emplacement, 'before_update')
def uppercase_code_emplacement(mapper, connection, target):
    if target.code_emplacement:
        target.code_emplacement = target.code_emplacement.upper()

class Article(Base):
    __tablename__ = "articles"
    
    id = Column(Integer, primary_key=True, index=True)
    code_article = Column(String, unique=True, nullable=False, index=True)
    produit_id = Column(Integer, ForeignKey("produits.id"), nullable=False)
    emplacement_id = Column(Integer, ForeignKey("emplacements.id"), nullable=False)
    quantite = Column(Integer, default=1)
    date_peremption = Column(DateTime, nullable=True)
    commentaire = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow, nullable=True)
    
    produit = relationship("Produit", back_populates="articles")
    emplacement = relationship("Emplacement", back_populates="articles")

# Event listener pour convertir code_article en majuscules
@event.listens_for(Article, 'before_insert')
@event.listens_for(Article, 'before_update')
def uppercase_code_article(mapper, connection, target):
    if target.code_article:
        target.code_article = target.code_article.upper()
