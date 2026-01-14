#!/bin/bash
# Script de démarrage DDB-Stock

cd /opt/ddb-stock
source venv/bin/activate

echo "🚀 Démarrage DDB-Stock API..."
echo "📡 API: http://$(hostname -I | awk '{print $1}'):8000"
echo "📚 Docs: http://$(hostname -I | awk '{print $1}'):8000/docs"
echo ""

uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
