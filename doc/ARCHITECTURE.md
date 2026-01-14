# 🏗️ Architecture Technique - DDB-Stock v2

## 📊 Vue d'Ensemble

DDB-Stock v2 est une application web de gestion d'inventaire domestique suivant une architecture **API REST** avec séparation frontend/backend.
```
┌─────────────────────────────────────────┐
│         Navigateur Web (Client)         │
│    HTML5 + JavaScript + Tailwind CSS    │
└──────────────┬──────────────────────────┘
               │ HTTP/REST
┌──────────────▼──────────────────────────┐
│       Backend API (FastAPI)             │
│    Python 3.11+ avec Uvicorn ASGI       │
└──────────────┬──────────────────────────┘
               │ SQLAlchemy ORM
┌──────────────▼──────────────────────────┐
│      Base de Données (SQLite)           │
│       Fichier : database.db             │
└─────────────────────────────────────────┘
```

---

## 🔧 Stack Technique

### Backend
- **Framework** : FastAPI 0.108.0
- **Serveur ASGI** : Uvicorn
- **ORM** : SQLAlchemy 2.0.23
- **Validation** : Pydantic 2.5.3
- **Base de données** : SQLite 3 (évolutif vers MariaDB)

### Frontend
- **Langage** : HTML5 + JavaScript (Vanilla)
- **Framework CSS** : Tailwind CSS 3.x (via CDN)
- **Communication** : Fetch API (REST)
- **Rendering** : Client-side (SPA partiel)

---

## 📁 Structure du Projet
```
/opt/ddb-stock/
├── venv/                       # Environnement virtuel Python
├── app/
│   ├── main.py                # Point d'entrée FastAPI
│   ├── database.py            # Configuration SQLAlchemy
│   ├── models.py              # Modèles ORM (tables)
│   ├── schemas.py             # Schémas Pydantic (validation)
│   └── routers/
│       ├── __init__.py
│       ├── produits.py        # Endpoints /produits
│       ├── emplacements.py    # Endpoints /emplacements
│       └── articles.py        # Endpoints /articles
├── web/
│   ├── index.html             # Dashboard
│   ├── produits.html          # Gestion produits
│   ├── emplacements.html      # Gestion emplacements
│   ├── articles.html          # Gestion articles
│   └── assets/
│       ├── app.js             # (Futur : JS commun)
│       └── style.css          # (Futur : CSS personnalisé)
├── data/
│   └── database.db            # Base SQLite
├── backups/                   # Sauvegardes automatiques
│   └── database_YYYYMMDD_HHMMSS.db
├── scripts/
│   ├── start.sh               # Script démarrage manuel
│   └── backup.sh              # Script backup
├── docs/                      # Documentation
├── requirements.txt           # Dépendances Python
├── README.md
├── INSTALLATION.md
├── ARCHITECTURE.md
└── .gitignore
```

---

## 🗄️ Modèle de Données

### Schéma Relationnel
```
┌─────────────────┐         ┌──────────────────┐
│    PRODUIT      │         │   EMPLACEMENT    │
├─────────────────┤         ├──────────────────┤
│ id (PK)         │         │ id (PK)          │
│ ean             │         │ code_emplacement │
│ nom             │         │ nom              │
│ marque          │         │ parent_id (FK)   │◄───┐
│ description     │         │ niveau           │    │
│ created_at      │         │ description      │    │
│ updated_at      │         │ created_at       │    │
└────────┬────────┘         │ updated_at       │    │
         │                  └────────┬─────────┘    │
         │                           │              │
         │                           │              │
         │    ┌──────────────────────┘              │
         │    │                                     │
         │    │                                     │
    ┌────▼────▼──────────┐                        │
    │      ARTICLE        │                        │
    ├─────────────────────┤                        │
    │ id (PK)             │                        │
    │ code_article        │                        │
    │ produit_id (FK)     │                        │
    │ emplacement_id (FK) │                        │
    │ quantite            │                        │
    │ date_peremption     │                        │
    │ commentaire         │                        │
    │ created_at          │                        │
    │ updated_at          │                        │
    └─────────────────────┘                        │
                                                    │
                  Hiérarchie parent ────────────────┘
```

### Relations
- **Produit** ↔ **Article** : One-to-Many (1 produit → N articles)
- **Emplacement** ↔ **Article** : One-to-Many (1 emplacement → N articles)
- **Emplacement** ↔ **Emplacement** : Self-referencing (parent_id)

---

## 🔄 Flux de Données

### Création d'un Article
```
1. Utilisateur remplit formulaire (web/articles.html)
2. JavaScript envoie POST /articles/ avec JSON
3. FastAPI reçoit et valide avec Pydantic (schemas.py)
4. SQLAlchemy insère dans table articles (models.py)
5. SQLite persiste les données (data/database.db)
6. FastAPI retourne JSON avec article créé
7. JavaScript met à jour l'interface
```

### Recherche avec Filtres
```
1. Utilisateur tape dans recherche
2. JavaScript filtre côté client (performances)
3. Pour filtres complexes : GET /articles/?emplacement_id=X
4. Backend filtre via SQLAlchemy
5. Résultats retournés en JSON
6. Affichage dans l'interface
```

---

## 🔐 Sécurité

### Validation des Données
- **Pydantic** : Validation de types, formats, contraintes
- **SQLAlchemy** : Protection injections SQL (ORM)
- **Regex** : Validation codes (EMP###, GG####)

### Intégrité Référentielle
- Clés étrangères (FK) avec contraintes
- Vérifications avant suppression
- Transactions atomiques

### Futures Améliorations
- [ ] Authentification JWT
- [ ] Rate limiting
- [ ] HTTPS (certificat SSL)
- [ ] CORS restreint

---

## 🚀 Performance

### Optimisations Actuelles
- **Eager loading** : Pas de N+1 queries
- **Indexation** : Index sur codes et clés étrangères
- **Cache client** : Données chargées une fois
- **Pagination** : Limitée à 100 par défaut

### Scalabilité
- **SQLite** : Suffisant jusqu'à ~100k articles
- **Migration MariaDB** : Changement 2 lignes dans database.py
- **Horizontal scaling** : Possibilité de load balancer

---

## 🧪 Tests

### Tests Manuels
- Swagger UI : `/docs`
- Interface web : tests fonctionnels

### Tests Futurs
- [ ] Tests unitaires (pytest)
- [ ] Tests d'intégration
- [ ] Tests E2E (Playwright)
- [ ] CI/CD (GitHub Actions)

---

## 📦 Déploiement

### Environnements

**Développement**
```bash
uvicorn app.main:app --reload
```

**Production**
```bash
systemctl start ddb-stock
```

**Docker** (futur)
```bash
docker-compose up -d
```

---

## 🔄 Migration Vers MariaDB

### Étapes

1. Installer MariaDB
```bash
sudo apt install mariadb-server
```

2. Créer base de données
```sql
CREATE DATABASE ddb_stock CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'ddb_user'@'localhost' IDENTIFIED BY 'password';
GRANT ALL PRIVILEGES ON ddb_stock.* TO 'ddb_user'@'localhost';
```

3. Modifier `app/database.py`
```python
# Remplacer
SQLALCHEMY_DATABASE_URL = "sqlite:///./data/database.db"

# Par
SQLALCHEMY_DATABASE_URL = "mysql+pymysql://ddb_user:password@localhost/ddb_stock"
```

4. Installer driver MySQL
```bash
pip install pymysql
```

5. Recréer les tables
```bash
# Les tables seront créées automatiquement au démarrage
```

---

## 📚 Documentation API

### Auto-générée
- **Swagger UI** : `/docs`
- **ReDoc** : `/redoc`
- **OpenAPI JSON** : `/openapi.json`

### Endpoints Principaux

**Produits**
- `GET /produits/` - Liste
- `POST /produits/` - Créer
- `GET /produits/{id}` - Détail
- `PUT /produits/{id}` - Modifier
- `DELETE /produits/{id}` - Supprimer

**Emplacements**
- `GET /emplacements/` - Liste
- `GET /emplacements/niveau/{n}` - Par niveau
- `GET /emplacements/{id}/enfants` - Sous-emplacements

**Articles**
- `GET /articles/` - Liste
- `GET /articles/peremption/prochaines` - Proche péremption
- `PATCH /articles/{id}/quantite` - Ajuster quantité

---

## 🛣️ Roadmap Technique

### Version 2.1
- Tests automatisés
- Logging structuré
- Métriques Prometheus

### Version 2.2
- Authentification JWT
- WebSockets (mises à jour temps réel)
- Cache Redis

### Version 3.0
- Microservices
- GraphQL API
- Event sourcing

---

**Architecture évolutive et maintenable ! 🏗️**