import tkinter as tk
from tkinter import messagebox
import time
import random
from faker import Faker
from sqlalchemy.orm import Session
from database import SessionLocal
from models import User, Product

fake = Faker()

def insert_data_postgresql():
    """Insère les données dans PostgreSQL et affiche le temps d'exécution."""
    try:
        num_users = int(user_entry.get())
        num_products = int(product_entry.get())
    except ValueError:
        messagebox.showerror("Erreur", "Veuillez entrer des nombres valides.")
        return

    start_time = time.time()
    db: Session = SessionLocal()

    # Insertion des utilisateurs
    users = [User(name=fake.name()) for _ in range(num_users)]
    db.bulk_save_objects(users)
    db.commit()

    # Insertion des produits
    products = [Product(name=fake.word(), price=round(random.uniform(5, 100), 2)) for _ in range(num_products)]
    db.bulk_save_objects(products)
    db.commit()

    end_time = time.time()
    db.close()

    execution_time = round(end_time - start_time, 2)
    
    # Ajouter le temps d'exécution dans l'historique
    history_text.insert(tk.END, f"PostgreSQL : {num_users} utilisateurs, {num_products} produits - {execution_time} sec\n")
    history_text.see(tk.END)  # Scroll automatique vers le bas
    
    messagebox.showinfo("PostgreSQL", f"Données insérées en {execution_time} secondes.")

def insert_data_neo4j():
    """Simule une insertion de données dans Neo4j (fonctionnalité à venir)."""
    try:
        num_users = int(user_entry.get())
        num_products = int(product_entry.get())
    except ValueError:
        messagebox.showerror("Erreur", "Veuillez entrer des nombres valides.")
        return

    start_time = time.time()

    # Simulation d’un temps d’insertion pour Neo4j (ajout réel plus tard)
    time.sleep(random.uniform(1, 3))  # Simule une exécution aléatoire entre 1 et 3 secondes

    end_time = time.time()
    execution_time = round(end_time - start_time, 2)

    # Ajouter le temps d'exécution dans l'historique
    history_text.insert(tk.END, f"Neo4j : {num_users} utilisateurs, {num_products} produits - {execution_time} sec\n")
    history_text.see(tk.END)  # Scroll automatique vers le bas
    
    messagebox.showinfo("Neo4j", f"Simulé : {execution_time} secondes.")

def show_data():
    """Récupère et affiche les utilisateurs et produits enregistrés dans PostgreSQL."""
    db: Session = SessionLocal()

    # Récupérer quelques utilisateurs et produits
    users = db.query(User).limit(10).all()
    products = db.query(Product).limit(10).all()

    db.close()

    # Construire une chaîne pour afficher les données
    result = "📌 **Utilisateurs (10 premiers)** :\n"
    result += "\n".join([f"- {user.id}: {user.name}" for user in users])
    result += "\n\n📌 **Produits (10 premiers)** :\n"
    result += "\n".join([f"- {product.id}: {product.name} ({product.price}€)" for product in products])

    # Afficher les données dans la zone d'historique
    history_text.insert(tk.END, result + "\n\n")
    history_text.see(tk.END)  # Scroll automatique vers le bas
# Création de la fenêtre principale
root = tk.Tk()
root.title("Génération de Données PostgreSQL & Neo4j")
root.geometry("500x400")

# Ajout de labels et entrées pour le nombre d’utilisateurs et de produits
tk.Label(root, text="Nombre d'Utilisateurs:").pack()
user_entry = tk.Entry(root)
user_entry.pack()

tk.Label(root, text="Nombre de Produits:").pack()
product_entry = tk.Entry(root)
product_entry.pack()

# Bouton pour générer les données dans PostgreSQL
generate_pg_button = tk.Button(root, text="Générer les Données (PostgreSQL)", command=insert_data_postgresql)
generate_pg_button.pack(pady=5)

# Bouton pour générer les données dans Neo4j (interface uniquement pour l'instant)
generate_neo4j_button = tk.Button(root, text="Générer les Données (Neo4j)", command=insert_data_neo4j)
generate_neo4j_button.pack(pady=5)

# Bouton pour afficher les données existantes
show_data_button = tk.Button(root, text="Afficher les Données", command=show_data)
show_data_button.pack(pady=5)
# Zone d'affichage des temps de performance
tk.Label(root, text="Historique des performances :").pack()
history_text = tk.Text(root, height=10, width=60)
history_text.pack()

# Lancer l'interface graphique
root.mainloop()