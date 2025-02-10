from neo4j import GraphDatabase

URI = "bolt://localhost:7687"  # À adapter si nécessaire
USER = "neo4j"
PASSWORD = "rootroot"

driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))

def get_driver():
    return driver

def close():
    driver.close()
