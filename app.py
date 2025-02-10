import tkinter as tk
from tkinter import messagebox, Toplevel
import time
import random
import time
from config import get_driver
from test import Neo4jManager
from faker import Faker
from sqlalchemy.orm import Session
from database import SessionLocal
from models import User, Product

fake = Faker()
driver = get_driver()
manager = Neo4jManager(driver)

def measure_time(func, *args):
    start_time = time.time()
    result = func(*args)
    end_time = time.time()
    print(f"{func.__name__} exécutée en {end_time - start_time:.2f} secondes")
    print(result)
    return result

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
    """Insère des utilisateurs, produits, relations follows et achats dans Neo4j."""
    try:
        num_users = int(user_entry.get())
        num_products = int(product_entry.get())
    except ValueError:
        messagebox.showerror("Erreur", "Veuillez entrer des nombres valides.")
        return
    
    start_time = time.time()
    
    # Création des index
    #manager.create_indexes()
    
    # Suppression des anciennes données (optionnel)
    manager.delete_all_data()
    
    # Insertion des utilisateurs et produits
    manager.create_users_and_products(num_users, num_products)
    
    # Création des relations follows et achats
    manager.create_relationships(num_users, num_products)
    
    execution_time = round(time.time() - start_time, 2)
    
    # Ajouter le temps d'exécution dans l'historique
    history_text.insert(tk.END, f"Neo4j : {num_users} utilisateurs, {num_products} produits - {execution_time} sec\n")
    history_text.see(tk.END)  # Scroll automatique vers le bas
    
    messagebox.showinfo("Neo4j", f"Insertion terminée en {execution_time} secondes.")


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

def count_users_postgresql():
    db: Session = SessionLocal()
    count = db.query(User).count()
    db.close()
    messagebox.showinfo("PostgreSQL", f"Nombre total d'utilisateurs : {count}")

def count_users_neo4j():
    count = measure_time(manager.count_users)
    messagebox.showinfo("Neo4j", f"Nombre total d'utilisateurs : {count}")

def count_products_postgresql():
    db: Session = SessionLocal()
    count = db.query(Product).count()
    db.close()
    messagebox.showinfo("PostgreSQL", f"Nombre total de produits : {count}")

def count_products_neo4j():
    count = measure_time(manager.count_follows)
    messagebox.showinfo("Neo4j", f"Nombre total de produits : {count}")


def open_popup(query_type):
    """Ouvre une fenêtre popup pour entrer les données nécessaires avant d'exécuter les requêtes."""
    popup = Toplevel(root)
    popup.title("Entrer les paramètres")

    tk.Label(popup, text="ID Utilisateur:").pack()
    user_id_entry = tk.Entry(popup)
    user_id_entry.pack()

    tk.Label(popup, text="Niveau Followers:").pack()
    level_entry = tk.Entry(popup)
    level_entry.pack()

    if query_type in ["followers_product", "buyers_count"]:
        tk.Label(popup, text="Nom du Produit:").pack()
        product_entry = tk.Entry(popup)
        product_entry.pack()
    else:
        product_entry = None

    tk.Button(popup, text="Exécuter", command=lambda: execute_queries(popup, query_type, user_id_entry, level_entry, product_entry)).pack(pady=5)

def execute_queries(popup, query_type, user_id_entry, level_entry, product_entry):
    """Exécute les requêtes pour PostgreSQL et Neo4j avec mesure du temps."""
    try:
        user_id = int(user_id_entry.get())
        level = int(level_entry.get())
        product_name = product_entry.get() if product_entry else None
    except ValueError:
        messagebox.showerror("Erreur", "Veuillez entrer des valeurs valides.")
        return

    popup.destroy()

    # Exécution des requêtes en fonction du type sélectionné
    if query_type == "products_by_followers":
        # Requête PostgreSQL
        try:
            db: Session = SessionLocal()
            start_time = time.time()
            products_pg = db.query(Product).filter(Product.id.in_(
                [p.id for p in db.query(User).filter(User.id == user_id)]
            )).all()
            pg_time = round(time.time() - start_time, 2)
            db.close()
        except Exception as e:
            products_pg = f"Erreur PostgreSQL: {str(e)}"
            pg_time = "N/A"

        # Requête Neo4j
        try:
            neo4j_start_time = time.time()
            products_neo4j = manager.get_products_by_followers_circle(user_id, level)
            neo4j_time = round(time.time() - neo4j_start_time, 2)
        except Exception as e:
            products_neo4j = f"Erreur Neo4j: {str(e)}"
            neo4j_time = "N/A"

        messagebox.showinfo("Résultat",
                            f"🔵 PostgreSQL ({pg_time} sec) : {products_pg}\n"
                            f"🟢 Neo4j ({neo4j_time} sec) : {products_neo4j}")

    elif query_type == "followers_product":
        try:
            followers_pg = []  # Simulation de requête PostgreSQL (à adapter)
            start_time = time.time()
            followers_pg_time = round(time.time() - start_time, 2)
        except Exception as e:
            followers_pg = f"Erreur PostgreSQL: {str(e)}"
            followers_pg_time = "N/A"

        try:
            neo4j_start_time = time.time()
            followers_neo4j = manager.get_products_by_followers_circle_for_product(user_id, level, product_name)
            neo4j_time = round(time.time() - neo4j_start_time, 2)
        except Exception as e:
            followers_neo4j = f"Erreur Neo4j: {str(e)}"
            neo4j_time = "N/A"

        messagebox.showinfo("Résultat",
                            f"🔵 PostgreSQL ({followers_pg_time} sec) : {followers_pg}\n"
                            f"🟢 Neo4j ({neo4j_time} sec) : {followers_neo4j}")

    elif query_type == "buyers_count":
        try:
            buyers_pg = []  # Simulation de requête PostgreSQL (à adapter)
            start_time = time.time()
            buyers_pg_time = round(time.time() - start_time, 2)
        except Exception as e:
            buyers_pg = f"Erreur PostgreSQL: {str(e)}"
            buyers_pg_time = "N/A"

        try:
            neo4j_start_time = time.time()
            buyers_neo4j = manager.get_product_purchase_by_followers_circle(product_name, level)
            neo4j_time = round(time.time() - neo4j_start_time, 2)
        except Exception as e:
            buyers_neo4j = f"Erreur Neo4j: {str(e)}"
            neo4j_time = "N/A"

        messagebox.showinfo("Résultat",
                            f"🔵 PostgreSQL ({buyers_pg_time} sec) : {buyers_pg}\n"
                            f"🟢 Neo4j ({neo4j_time} sec) : {buyers_neo4j}")



root = tk.Tk()
root.title("Génération de Données PostgreSQL & Neo4j")
root.geometry("700x500")

# Ajout de labels et entrées pour le nombre d’utilisateurs et de produits
tk.Label(root, text="Nombre d'Utilisateurs:").pack()
user_entry = tk.Entry(root)
user_entry.pack()

tk.Label(root, text="Nombre de Produits:").pack()
product_entry = tk.Entry(root)
product_entry.pack()


button_frame = tk.Frame(root)
button_frame.pack(pady=10)

# PostgreSQL
pg_frame = tk.Frame(button_frame)
pg_frame.pack(side=tk.LEFT, padx=10)

tk.Label(pg_frame, text="PostgreSQL").pack()
tk.Button(pg_frame, text="Générer Données", command=insert_data_postgresql).pack(pady=2)
tk.Button(pg_frame, text="Compter Utilisateurs", command=count_users_postgresql).pack(pady=2)
tk.Button(pg_frame, text="Compter Produits", command=count_products_postgresql).pack(pady=2)


# Neo4j
neo4j_frame = tk.Frame(button_frame)
neo4j_frame.pack(side=tk.RIGHT, padx=10)

tk.Label(neo4j_frame, text="Neo4j").pack()
tk.Button(neo4j_frame, text="Générer Données", command=insert_data_neo4j).pack(pady=2)
tk.Button(neo4j_frame, text="Compter Utilisateurs", command=count_users_neo4j).pack(pady=2)
tk.Button(neo4j_frame, text="Compter Produits", command=count_products_neo4j).pack(pady=2)

tk.Button(root, text="Produits achetés par les followers", command=lambda: open_popup("products_by_followers")).pack(pady=5)
tk.Button(root, text="Followers ayant acheté un produit", command=lambda: open_popup("followers_product")).pack(pady=5)
tk.Button(root, text="Nombre d'acheteurs d'un produit", command=lambda: open_popup("buyers_count")).pack(pady=5)


tk.Button(root, text="Afficher les Données", command=show_data).pack(pady=5)


# Zone d'affichage des temps de performance
tk.Label(root, text="Historique des performances :").pack()
history_text = tk.Text(root, height=10, width=60)
history_text.pack()

# Lancer l'interface graphique
root.mainloop()