#!/bin/bash

# Backup
cp /opt/ddb-stock/web-mobile/entree.html /opt/ddb-stock/web-mobile/entree.html.bak

# Dans creerProduitDepuisWeb, ajouter image_url
sed -i 's/"description": product\.description/"description": product.description,\n                "image_url": product.image_url || null/' /opt/ddb-stock/web-mobile/entree.html

echo "✅ entree.html patché pour supporter les images"
