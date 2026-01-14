# 📦 Guide d'Installation - DDB-Stock v2

## 🎯 Installation sur Debian 12 / Ubuntu 22.04+

### Étape 1 : Prérequis Système
```bash
# Mise à jour système
sudo apt update && sudo apt upgrade -y

# Installer Python et outils
sudo apt install -y python3 python3-venv python3-pip git curl sqlite3
```

### Étape 2 : Cloner le Projet
```bash
# Créer dossier de destination
sudo mkdir -p /opt/ddb-stock
sudo chown $USER:$USER /opt/ddb-stock

# Cloner depuis Git
cd /opt
git clone https://github.com/votre-username/ddb-stock-v2.git ddb-stock
cd ddb-stock
```

### Étape 3 : Configuration Python
```bash
# Créer environnement virtuel
python3 -m venv venv

# Activer environnement
source venv/bin/activate

# Installer dépendances
pip install --upgrade pip
pip install -r requirements.txt
```

### Étape 4 : Initialisation Base de Données
```bash
# Les tables seront créées automatiquement au premier démarrage
# La base SQLite sera créée dans : /opt/ddb-stock/data/database.db
```

### Étape 5 : Test Manuel
```bash
# Lancer le serveur
uvicorn app.main:app --host 0.0.0.0 --port 8000

# Accéder à l'application
# http://VOTRE-IP:8000/web/
# http://VOTRE-IP:8000/docs (Swagger)
```

---

## 🔧 Installation comme Service Systemd

### Créer le Service
```bash
sudo nano /etc/systemd/system/ddb-stock.service
```

**Contenu du fichier** :
```ini
[Unit]
Description=DDB-Stock API Service
After=network.target

[Service]
Type=simple
User=votre-utilisateur
Group=votre-utilisateur
WorkingDirectory=/opt/ddb-stock
Environment="PATH=/opt/ddb-stock/venv/bin"
ExecStart=/opt/ddb-stock/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### Activer et Démarrer
```bash
# Recharger systemd
sudo systemctl daemon-reload

# Activer au démarrage
sudo systemctl enable ddb-stock

# Démarrer le service
sudo systemctl start ddb-stock

# Vérifier le statut
sudo systemctl status ddb-stock
```

---

## 📅 Configuration des Backups Automatiques

### Créer le Script de Backup

Le script est déjà dans `scripts/backup.sh`. Rendre exécutable :
```bash
chmod +x /opt/ddb-stock/scripts/backup.sh
```

### Configurer Cron
```bash
# Éditer crontab
crontab -e

# Ajouter cette ligne (backup tous les jours à 2h)
0 2 * * * /opt/ddb-stock/scripts/backup.sh >> /opt/ddb-stock/backups/backup.log 2>&1
```

---

## 🔥 Configuration Firewall (Optionnel)
```bash
# Installer UFW
sudo apt install ufw

# Autoriser SSH
sudo ufw allow 22/tcp

# Autoriser port 8000 (API)
sudo ufw allow 8000/tcp

# Activer firewall
sudo ufw enable
```

---

## 🐋 Installation avec Docker (Optionnel)
```bash
# Construction de l'image
docker build -t ddb-stock:latest .

# Lancer le conteneur
docker run -d \
  --name ddb-stock \
  -p 8000:8000 \
  -v /opt/ddb-stock/data:/app/data \
  -v /opt/ddb-stock/backups:/app/backups \
  --restart always \
  ddb-stock:latest
```

---

## ✅ Vérification de l'Installation

### Tests API
```bash
# Test de santé
curl http://localhost:8000/health

# Résultat attendu : {"status":"ok","version":"2.0.0"}

# Test liste produits
curl http://localhost:8000/produits/

# Résultat attendu : []
```

### Tests Interface Web

1. Ouvrir navigateur : `http://VOTRE-IP:8000/web/`
2. Créer un produit
3. Créer un emplacement
4. Créer un article

---

## 🔧 Dépannage

### Erreur : Port 8000 déjà utilisé
```bash
# Trouver le processus
sudo lsof -i :8000

# Tuer le processus
sudo kill -9 PID
```

### Erreur : Permission denied sur database.db
```bash
# Corriger les permissions
sudo chown -R $USER:$USER /opt/ddb-stock/data/
sudo chmod 755 /opt/ddb-stock/data/
```

### Erreur : Module not found
```bash
# Réinstaller les dépendances
cd /opt/ddb-stock
source venv/bin/activate
pip install --force-reinstall -r requirements.txt
```

---

## 📊 Prochaines Étapes

1. ✅ Installation terminée
2. 📖 Lire [UTILISATION.md](UTILISATION.md)
3. 🏗️ Consulter [ARCHITECTURE.md](ARCHITECTURE.md)
4. 🚀 Commencer à utiliser l'application

---

**Installation réussie ! 🎉**