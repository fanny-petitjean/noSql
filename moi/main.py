import time
from config import get_driver
from test2 import Neo4jManager

def measure_time(func, *args):
    start_time = time.time()
    result = func(*args)
    end_time = time.time()
    print(f"{func.__name__} exécutée en {end_time - start_time:.2f} secondes")
    print(result)
    return result


if __name__ == "__main__":
    driver = get_driver()
    manager = Neo4jManager(driver)

    while True:
        print("\n1 - Ajouter des utilisateurs et produits")
        print("2 - Nombre d'utilisateurs")
        print("3 - Nombre de produits")
        print("4 - Nombre de relations FOLLOWS")
        print("5 - Nombre d'achats")
        print("6 - Liste des produits achetés par les cercles de followers")
        print("7 - Liste des followers ayant acheté un produit spécifique")
        print("8 - Nombre d'acheteurs d'un produit dans un cercle de followers")
        print("9 - Quitter")
        choice = input("Choisissez une option : ")

        if choice == "1":
            num_users = int(input("Combien d'utilisateurs pour les achats ? "))
            num_products = int(input("Combien de produits ? "))
            manager.create_indexes()  # 🔹 Vérifie/crée les index
            # Supprimer les anciennes données avant d'insérer (optionnel)
            manager.delete_all_data()
            start_time = time.time()

            # ⚠️ Tester d'abord avec 100K users et 10K produits
            manager.create_users_and_products(num_users, num_products)
            manager.create_relationships(num_users, num_products)

            print(f"🔥 Temps total d'exécution : {time.time() - start_time:.2f} sec.")

        elif choice == "2":
            user_count = measure_time(manager.count_users)
            print(f"Nombre d'utilisateurs : {user_count}")
        elif choice == "3":
            product_count = measure_time(manager.count_products)
            print(f"Nombre de produits : {product_count}")
        elif choice == "4":
            follow_count = measure_time(manager.count_follows)
            print(f"Nombre de relations FOLLOWS : {follow_count}")
        elif choice == "5":
            purchase_count = measure_time(manager.count_purchases)
            print(f"Nombre d'achats : {purchase_count}")
        elif choice == "6":
            user_id = int(input("Entrez l'ID de l'utilisateur : "))
            level = int(input("Entrez le niveau des followers (1, 2, etc.) : "))
            products = measure_time(manager.get_products_by_followers_circle, user_id, level)
            print(f"Produits achetés par les cercles de followers : {products}")
        elif choice == "7":
            user_id = int(input("Entrez l'ID de l'utilisateur : "))
            level = int(input("Entrez le niveau des followers (1, 2, etc.) : "))
            product_name = input("Entrez le nom du produit : ")
            followers_and_products = measure_time(manager.get_products_by_followers_circle_for_product, user_id, level, product_name)
            print(f"Followers ayant acheté le produit '{product_name}' : {followers_and_products}")
        elif choice == "8":
            product_id = int(input("Entrez l'ID du produit : "))
            level = int(input("Entrez le niveau des followers (0, 1, 2, etc.) : "))
            buyers_count = measure_time(manager.get_product_purchase_by_followers_circle, product_id, level)
            print(f"Nombre d'acheteurs du produit dans un cercle de followers de niveau {level} : {buyers_count}")
        elif choice == "9":
            driver.close()
            break
        else:
            print("Option invalide")
