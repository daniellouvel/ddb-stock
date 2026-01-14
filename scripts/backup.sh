#!/bin/bash
# Backup automatique de la base SQLite

DATE=$(date +%Y%m%d_%H%M%S)
SOURCE="/opt/ddb-stock/data/database.db"
DEST="/opt/ddb-stock/backups/database_${DATE}.db"

if [ -f "$SOURCE" ]; then
    cp "$SOURCE" "$DEST"
    echo "✅ Backup créé: $DEST"
    
    # Garder seulement les 30 derniers backups
    cd /opt/ddb-stock/backups
    ls -t database_*.db | tail -n +31 | xargs -r rm
    echo "🧹 Anciens backups nettoyés"
else
    echo "❌ Base de données introuvable"
fi
