import sqlite3

conn = sqlite3.connect('/opt/ddb-stock/stock.db')
cursor = conn.cursor()

try:
    cursor.execute('ALTER TABLE produits ADD COLUMN image_url TEXT')
    conn.commit()
    print("✅ Colonne image_url ajoutée avec succès")
except sqlite3.OperationalError as e:
    if "duplicate column name" in str(e):
        print("ℹ️ Colonne image_url existe déjà")
    else:
        print(f"❌ Erreur: {e}")

conn.close()
