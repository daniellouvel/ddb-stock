from fastapi import APIRouter, HTTPException
import httpx
import os

router = APIRouter(prefix="/recherche-ean", tags=["Recherche EAN"])

BARCODELOOKUP_API_KEY = os.getenv("BARCODELOOKUP_API_KEY", "gzk47hty1h9qbw6b4t1nqcqrg75pwu")

@router.get("/{ean}")
async def rechercher_ean(ean: str):
    """Rechercher un produit par son code EAN via OpenFoodFacts puis Barcodelookup"""
    
    # 1. Essayer OpenFoodFacts d'abord (gratuit, illimité)
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://world.openfoodfacts.org/api/v0/product/{ean}.json",
                timeout=5.0
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == 1:
                    product = data.get("product", {})
                    
                    return {
                        "source": "OpenFoodFacts",
                        "nom": product.get("product_name") or product.get("product_name_fr") or "Produit sans nom",
                        "marque": product.get("brands"),
                        "description": product.get("generic_name") or product.get("categories")
                    }
    except Exception as e:
        print(f"Erreur OpenFoodFacts: {e}")
    
    # 2. Essayer Barcodelookup (100 requêtes/jour)
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://api.barcodelookup.com/v3/products",
                params={"barcode": ean, "key": BARCODELOOKUP_API_KEY},
                timeout=5.0
            )
            
            if response.status_code == 200:
                data = response.json()
                products = data.get("products", [])
                
                if products:
                    product = products[0]
                    
                    return {
                        "source": "Barcodelookup",
                        "nom": product.get("title") or product.get("product_name") or "Produit sans nom",
                        "marque": product.get("brand") or product.get("manufacturer"),
                        "description": product.get("description") or product.get("category")
                    }
    except Exception as e:
        print(f"Erreur Barcodelookup: {e}")
    
    # Aucune source n'a trouvé le produit
    raise HTTPException(status_code=404, detail="Produit non trouvé")
