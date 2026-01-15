from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine, Base
from app.routers import produits, emplacements, articles

# Créer les tables
Base.metadata.create_all(bind=engine)

# Créer application FastAPI
app = FastAPI(
    title="DDB-Stock API",
    description="API de gestion d'inventaire domestique",
    version="2.0.0"
)

# CORS (pour permettre accès depuis navigateur)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclure routers
app.include_router(produits.router)
app.include_router(emplacements.router)
app.include_router(articles.router)

# Servir fichiers statiques (frontend)
app.mount("/web", StaticFiles(directory="/opt/ddb-stock/web", html=True), name="web")
app.mount("/web-mobile", StaticFiles(directory="web-mobile"), name="web-mobile")

@app.get("/")
def root():
    return {
        "message": "DDB-Stock API v2",
        "docs": "/docs",
        "redoc": "/redoc",
        "frontend": "/web",
        "endpoints": {
            "produits": "/produits",
            "emplacements": "/emplacements",
            "articles": "/articles"
        }
    }

@app.get("/health")
def health_check():
    return {"status": "ok", "version": "2.0.0"}
