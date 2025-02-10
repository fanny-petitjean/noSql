import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))  # Ajoute le dossier actuel au PATH

from faker import Faker
from sqlalchemy.orm import Session
from models import User, Product, Purchase, Follower
from database import SessionLocal
import random

fake = Faker()

def populate_database():
    db: Session = SessionLocal()
    
    # Création des utilisateurs
    users = [User(name=fake.name()) for _ in range(1000)]
    db.add_all(users)
    db.commit()

    # Création des produits
    products = [Product(name=fake.word(), price=round(random.uniform(5, 100), 2)) for _ in range(100)]
    db.add_all(products)
    db.commit()

    # Ajout des followers (relations aléatoires)
    user_ids = [user.id for user in db.query(User).all()]
    for user_id in user_ids:
        followers = random.sample(user_ids, random.randint(0, 20))
        for follower_id in followers:
            if user_id != follower_id:  # Eviter qu'un utilisateur se suive lui-même
                db.add(Follower(user_id=user_id, follower_id=follower_id))
    db.commit()

    # Ajout des achats aléatoires
    product_ids = [product.id for product in db.query(Product).all()]
    for user_id in user_ids:
        purchases = random.sample(product_ids, random.randint(0, 5))
        for product_id in purchases:
            db.add(Purchase(user_id=user_id, product_id=product_id))
    db.commit()

    db.close()
    print("✅ Base de données remplie avec succès !")

if __name__ == "__main__":
    populate_database()