from fastapi import APIRouter, HTTPException
import httpx

router = APIRouter(prefix="/recherche-ean", tags=["Recherche EAN"])

BARCODE_API_KEY = "8y6svkw7q3hszpon8rsedgn9zbjkes"

@router.get("/{ean}")
async def rechercher_ean(ean: str):
    """Recherche un EAN sur les API externes"""
    
    # 1. OpenFoodFacts
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://world.openfoodfacts.org/api/v0/product/{ean}.json",
                timeout=5.0
            )
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == 1 and data.get("product", {}).get("product_name"):
                    product = data["product"]
                    return {
                        "source": "OpenFoodFacts",
                        "nom": product.get("product_name"),
                        "marque": product.get("brands"),
                        "description": product.get("categories")
                    }
    except Exception as e:
        print(f"OpenFoodFacts error: {e}")
    
    # 2. Barcodelookup
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://api.barcodelookup.com/v3/products?barcode={ean}&key={BARCODE_API_KEY}",
                timeout=5.0
            )
            if response.status_code == 200:
                data = response.json()
                if data.get("products") and len(data["products"]) > 0:
                    product = data["products"][0]
                    return {
                        "source": "Barcodelookup",
                        "nom": product.get("title") or product.get("product_name") or "Produit sans nom",
                        "marque": product.get("brand") or product.get("manufacturer"),
                        "description": product.get("description") or product.get("category")
                    }
    except Exception as e:
        print(f"Barcodelookup error: {e}")
    
    # 3. Non trouvé
    raise HTTPException(status_code=404, detail="EAN non trouvé")
