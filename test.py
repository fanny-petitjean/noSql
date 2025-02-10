import random
import time
import neo4j  # Ajoutez ceci en haut de votre fichier
from faker import Faker
class Neo4jManager:
    def __init__(self, driver):
        self.driver = driver
        self.fake = Faker()
    
    def create_indexes(self):
        """Crée des index pour optimiser les requêtes sur les propriétés fréquemment utilisées"""
        with self.driver.session() as session:
            print("🔄 Création des index sur les propriétés 'id' des utilisateurs et des produits...")

            # Création d'un index sur l'ID des utilisateurs
            session.run("""
                CREATE INDEX IF NOT EXISTS FOR (u:User) ON (u.id)
            """)

            # Création d'un index sur l'ID des produits
            session.run("""
                CREATE INDEX IF NOT EXISTS FOR (p:Product) ON (p.id)
            """)

            print("✅ Index créés.")


    def delete_all_data(self):
        """Supprime toutes les données (utilisateurs, produits, relations) en batchs optimisés"""
        batch_size = 10_000  # Ajuste la taille du batch en fonction de ta performance
        with self.driver.session() as session:
            print("🔄 Suppression des nœuds et relations...")

            # Supprimer tous les produits et utilisateurs par lots de 10 000
            product_ids = [record["id"] for record in session.run("""
                MATCH (p:Product)
                RETURN p.id AS id
            """)]

            user_ids = [record["id"] for record in session.run("""
                MATCH (u:User)
                RETURN u.id AS id
            """)]

            # Supprimer les produits
            for i in range(0, len(product_ids), batch_size):
                session.execute_write(lambda tx: tx.run("""
                    UNWIND $product_ids AS id
                    MATCH (p:Product {id: id})
                    DETACH DELETE p
                """, product_ids=product_ids[i:i + batch_size]))

            # Supprimer les utilisateurs
            for i in range(0, len(user_ids), batch_size):
                session.execute_write(lambda tx: tx.run("""
                    UNWIND $user_ids AS id
                    MATCH (u:User {id: id})
                    DETACH DELETE u
                """, user_ids=user_ids[i:i + batch_size]))

            print("✅ Toutes les données ont été supprimées.")



    def create_users_and_products(self, num_users, num_products):
        """Insère les utilisateurs et produits en batch optimisé"""
        start_time = time.time()
        batch_size = 5_000

        with self.driver.session() as session:
            print("🔄 Insertion des utilisateurs...")
            users = [{"id": j, "name": self.fake.name()} for j in range(num_users)]
            for i in range(0, num_users, batch_size):
                session.execute_write(lambda tx: tx.run("""
                    UNWIND $users AS user
                    MERGE (u:User {id: user.id})
                    SET u.name = user.name
                """, users=users[i:i + batch_size]))

            print("🔄 Insertion des produits...")
            products = [{"id": j, "name": self.fake.word()} for j in range(num_products)]
            for i in range(0, num_products, batch_size):
                session.execute_write(lambda tx: tx.run("""
                    UNWIND $products AS product
                    MERGE (p:Product {id: product.id})
                    SET p.name = product.name
                """, products=products[i:i + batch_size]))

        print(f"✅ Utilisateurs et produits insérés en {time.time() - start_time:.2f} sec.")

    def create_relationships(self, num_users, num_products):
        """Crée les relations FOLLOWS et BOUGHT en batch optimisé"""
        start_time = time.time()
        batch_size = 5_000

        with self.driver.session() as session:
            print("🔄 Insertion des relations FOLLOWS...")
            follows = [{"user_id": user_id, "follower_id": f}
                       for user_id in range(num_users)
                       for f in random.sample(range(num_users), random.randint(0, min(20, num_users - 1))) if f != user_id]
            
            for i in range(0, len(follows), batch_size):
                session.execute_write(lambda tx: tx.run("""
                    UNWIND $follows AS f
                    MATCH (u1:User {id: f.user_id})
                    MATCH (u2:User {id: f.follower_id})
                    MERGE (u1)-[:FOLLOWS]->(u2)
                """, follows=follows[i:i + batch_size]))

            print("🔄 Insertion des relations BOUGHT...")
            purchases = [{"user_id": user_id, "product_id": p}
                         for user_id in range(num_users)
                         for p in random.sample(range(num_products), random.randint(0, 5))]
            
            for i in range(0, len(purchases), batch_size):
                session.execute_write(lambda tx: tx.run("""
                    UNWIND $purchases AS p
                    MATCH (u:User {id: p.user_id})
                    MATCH (pr:Product {id: p.product_id})
                    MERGE (u)-[:BOUGHT]->(pr)
                """, purchases=purchases[i:i + batch_size]))

        print(f"✅ Relations insérées en {time.time() - start_time:.2f} sec.")

    def get_followers_purchases(self, user_id):
        query = """
        MATCH (u:User {id: $user_id})-[:FOLLOWS]->(f:User)-[:BOUGHT]->(p:Product)
        RETURN f.name AS follower, p.name AS product
        """
        with self.driver.session() as session:
            result = session.run(query, user_id=user_id)
            return [(record["follower"], record["product"]) for record in result]

    def get_viral_products(self):
        query = """
        MATCH (p:Product)<-[:BOUGHT]-(u:User)
        RETURN p.name AS product, count(u) AS num_purchases
        ORDER BY num_purchases DESC
        LIMIT 5
        """
        with self.driver.session() as session:
            result = session.run(query)
            return [(record["product"], record["num_purchases"]) for record in result]

    def count_users(self):
        with self.driver.session() as session:
            return session.run("MATCH (u:User) RETURN count(u)").single()[0]

    def count_products(self):
        with self.driver.session() as session:
            return session.run("MATCH (p:Product) RETURN count(p)").single()[0]

    def count_follows(self):
        with self.driver.session() as session:
            return session.run("MATCH ()-[r:FOLLOWS]->() RETURN count(r)").single()[0]

    def count_purchases(self):
        with self.driver.session() as session:
            return session.run("MATCH ()-[r:BOUGHT]->() RETURN count(r)").single()[0]

    def get_products_by_followers_circle(self, user_id, level):
        query = f"""
        MATCH (u:User {{id: $user_id}})-[:FOLLOWS*1..{level}]->(f:User)-[:BOUGHT]->(p:Product)
        RETURN p.name AS product, COUNT(DISTINCT f) AS num_buyers
        ORDER BY num_buyers DESC
        """
        with self.driver.session() as session:
            result = session.run(query, user_id=user_id)
            return [(record["product"], record["num_buyers"]) for record in result]

    def get_products_by_followers_circle_for_product(self, user_id, level, product_name):
        query = f"""
        MATCH (u:User {{id: $user_id}})-[:FOLLOWS*1..{level}]->(f:User)-[:BOUGHT]->(p:Product {{name: $product_name}})
        RETURN f.id AS follower_id, f.name AS follower_name
        """
        with self.driver.session() as session:
            result = session.run(query, user_id=user_id, product_name=product_name)
            return [(record["follower_id"], record["follower_name"]) for record in result]


    def get_product_purchase_by_followers_circle(self, product_id, level):
        query = f"""
        MATCH (u:User)-[:FOLLOWS*1..{level}]->(f:User)-[:BOUGHT]->(p:Product {{id: $product_id}})
        RETURN COUNT(DISTINCT f) AS num_buyers
        """
        with self.driver.session() as session:
            result = session.run(query, product_id=product_id)
            return result.single()["num_buyers"]
