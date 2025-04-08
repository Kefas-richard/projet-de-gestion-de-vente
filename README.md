# projet-de-gestion-de-vente
gestion de vente

## 📊 Résultats  
![CA Mensuel](reports/ca_mensuel.png)  
*Légende : Pic de ventes en décembre (effet fêtes)*  

## 🛠 Installation  
```bash
# Clonez le dépôt
git clone (https://github.com/Kefas-richard/projet-de-gestion-de-vente)

# Installez les dépendances
pip install -r requirements.txt

# Générer la base de données
python scripts/create_db.py

# lancer l'analyse
python scripts/analyse_ventes.py

# Lancer le dashboard
python scripts/dashboard.py
