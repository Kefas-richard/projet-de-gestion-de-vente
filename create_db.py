import sqlite3
import random
from datetime import datetime
import os
from faker import Faker

fake = Faker('fr_FR')

def init_db():
    """Initialise la base de données avec des données de démonstration."""
    
    # Configuration des chemins
    db_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'ventes_magasin.db')
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    try:
        # Connexion à la base de données
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        
        # Création des tables
        c.execute('''CREATE TABLE IF NOT EXISTS produits
                    (id INTEGER PRIMARY KEY, 
                     nom TEXT NOT NULL, 
                     categorie TEXT CHECK(categorie IN ('Informatique', 'Mobile', 'Audio', 'Maison', 'Bureau')),
                     prix_unitaire REAL NOT NULL CHECK(prix_unitaire > 0))''')
        
        c.execute('''CREATE TABLE IF NOT EXISTS clients
                    (id INTEGER PRIMARY KEY, 
                     nom TEXT NOT NULL, 
                     email TEXT UNIQUE,
                     ville TEXT)''')
        
        c.execute('''CREATE TABLE IF NOT EXISTS ventes
                    (id INTEGER PRIMARY KEY,
                     produit_id INTEGER NOT NULL,
                     client_id INTEGER NOT NULL,
                     date TEXT NOT NULL,
                     quantite INTEGER NOT NULL CHECK(quantite > 0),
                     montant REAL NOT NULL,
                     FOREIGN KEY(produit_id) REFERENCES produits(id),
                     FOREIGN KEY(client_id) REFERENCES clients(id))''')
        
        # Nettoyage des anciennes données
        c.execute("DELETE FROM produits")
        c.execute("DELETE FROM clients")
        c.execute("DELETE FROM ventes")
        
        # Insertion de produits
        produits = [
            (1, "Laptop Elite", "Informatique", 999.99),
            (2, "Smartphone Pro", "Mobile", 799.99),
            (3, "Casque Audio", "Audio", 149.99),
            (4, "Clavier Mécanique", "Informatique", 89.99),
            (5, "Souris Gaming", "Informatique", 59.99),
            (6, "Enceinte Bluetooth", "Audio", 129.99),
            (7, "Lampe LED", "Maison", 39.99),
            (8, "Cahier Premium", "Bureau", 19.99),
            (9, "Stylo 3D", "Bureau", 29.99),
            (10, "Tapis de Souris", "Informatique", 24.99)
        ]
        c.executemany("INSERT INTO produits VALUES (?,?,?,?)", produits)
        
        # Insertion de clients
        clients = [(i, fake.name(), fake.unique.email(), fake.city()) for i in range(1, 21)]
        c.executemany("INSERT INTO clients VALUES (?,?,?,?)", clients)
        
        # Génération de ventes
        for i in range(1, 201):
            date = fake.date_between(start_date='-2y', end_date='today').strftime("%Y-%m-%d")
            produit_id = random.randint(1, 10)
            client_id = random.randint(1, 20)
            quantite = random.randint(1, 5)
            
            c.execute("SELECT prix_unitaire FROM produits WHERE id=?", (produit_id,))
            prix = c.fetchone()[0]
            
            # CORRECTION ICI : Parenthèses bien placées
            remise = random.choice([0, 0, 0, 0.1, 0.15])
            montant = round(prix * quantite * (1 - remise), 2)
            
            c.execute("INSERT INTO ventes VALUES (?,?,?,?,?,?)",
                     (i, produit_id, client_id, date, quantite, montant))
        
        conn.commit()
        print("Base initialisée avec succès : 10 produits, 20 clients, 200 ventes")
        
    except Exception as e:
        print(f"Erreur lors de l'initialisation : {str(e)}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    init_db()