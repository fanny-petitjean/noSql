import time
from sqlalchemy.orm import Session
from database import SessionLocal
from models import User, Product, Purchase, Follower

def measure_query_time(query_function, *args):
    """Mesure le temps d'exécution d'une requête."""
    start_time = time.time()
    result = query_function(*args)
    end_time = time.time()
    print(f"⏱ Temps d'exécution : {end_time - start_time:.5f} secondes")
    return result

def get_user_purchases(user_id):
    """Obtenir la liste des produits achetés par un utilisateur."""
    db: Session = SessionLocal()
    purchases = (
        db.query(Product.name, Product.price)
        .join(Purchase)
        .filter(Purchase.user_id == user_id)
        .all()
    )
    db.close()
    return purchases

def get_follower_purchases(user_id, depth=1):
    """Obtenir la liste des produits achetés par les followers d’un utilisateur (jusqu'à un niveau n)."""
    db: Session = SessionLocal()
    
    followers = set([user_id])
    for _ in range(depth):
        new_followers = set(
            db.query(Follower.follower_id)
            .filter(Follower.user_id.in_(followers))
            .all()
        )
        followers.update([f[0] for f in new_followers])

    purchases = (
        db.query(Product.name, Product.price)
        .join(Purchase)
        .filter(Purchase.user_id.in_(followers))
        .all()
    )
    
    db.close()
    return purchases

def get_product_virality(product_id, depth=1):
    """Obtenir le nombre de followers ayant acheté un produit donné."""
    db: Session = SessionLocal()

    followers = set()
    current_followers = (
        db.query(Follower.follower_id)
        .filter(Follower.user_id == product_id)
        .all()
    )
    followers.update([f[0] for f in current_followers])

    for _ in range(depth - 1):
        next_followers = (
            db.query(Follower.follower_id)
            .filter(Follower.user_id.in_(followers))
            .all()
        )
        followers.update([f[0] for f in next_followers])

    purchase_count = (
        db.query(Purchase.user_id)
        .filter(Purchase.user_id.in_(followers), Purchase.product_id == product_id)
        .count()
    )
    
    db.close()
    return purchase_count

if __name__ == "__main__":
    user_id_test = 1
    product_id_test = 5

    print("🔍 Produits achetés par l'utilisateur", user_id_test)
    measure_query_time(get_user_purchases, user_id_test)

    print("\n🔍 Produits achetés par les followers de l'utilisateur", user_id_test)
    measure_query_time(get_follower_purchases, user_id_test, 2)

    print("\n🔍 Popularité du produit", product_id_test)
    measure_query_time(get_product_virality, product_id_test, 2)