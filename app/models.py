from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Produit(Base):
    __tablename__ = "produits"
    
    id = Column(Integer, primary_key=True, index=True)
    ean = Column(String(13), unique=True, nullable=True, index=True)
    nom = Column(String(255), nullable=False)
    marque = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relations
    articles = relationship("Article", back_populates="produit")

class Emplacement(Base):
    __tablename__ = "emplacements"
    
    id = Column(Integer, primary_key=True, index=True)
    code_emplacement = Column(String(10), unique=True, nullable=False, index=True)
    nom = Column(String(100), nullable=False)
    parent_id = Column(Integer, ForeignKey("emplacements.id"), nullable=True)
    niveau = Column(Integer, default=1)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relations
    articles = relationship("Article", back_populates="emplacement")
    parent = relationship("Emplacement", remote_side=[id], backref="enfants")

class Article(Base):
    __tablename__ = "articles"
    
    id = Column(Integer, primary_key=True, index=True)
    code_article = Column(String(10), unique=True, nullable=False, index=True)
    produit_id = Column(Integer, ForeignKey("produits.id"), nullable=False)
    emplacement_id = Column(Integer, ForeignKey("emplacements.id"), nullable=False)
    quantite = Column(Integer, default=1, nullable=False)
    date_peremption = Column(DateTime(timezone=True), nullable=True)
    commentaire = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relations
    produit = relationship("Produit", back_populates="articles")
    emplacement = relationship("Emplacement", back_populates="articles")
