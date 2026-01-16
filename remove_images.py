import sqlite3

conn = sqlite3.connect('/opt/ddb-stock/data/database.db')
cursor = conn.cursor()

try:
    # Créer une nouvelle table sans image_url
    cursor.execute('''
        CREATE TABLE produits_new (
            id INTEGER PRIMARY KEY,
            ean TEXT UNIQUE,
            nom TEXT NOT NULL,
            marque TEXT,
            description TEXT,
            created_at TIMESTAMP,
            updated_at TIMESTAMP
        )
    ''')
    
    # Copier les données (sans image_url)
    cursor.execute('''
        INSERT INTO produits_new (id, ean, nom, marque, description, created_at, updated_at)
        SELECT id, ean, nom, marque, description, created_at, updated_at
        FROM produits
    ''')
    
    # Supprimer l'ancienne table
    cursor.execute('DROP TABLE produits')
    
    # Renommer la nouvelle table
    cursor.execute('ALTER TABLE produits_new RENAME TO produits')
    
    conn.commit()
    print("✅ Colonne image_url supprimée avec succès")
except Exception as e:
    print(f"❌ Erreur: {e}")
    conn.rollback()

conn.close()
