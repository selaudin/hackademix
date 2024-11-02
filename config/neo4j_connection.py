import os
from neo4j import GraphDatabase

def get_neo4j_connection():
    # Load the password from an environment variable
    neo4j_password = os.getenv('NEO4J_PASSWORD')

    if not neo4j_password:
        raise ValueError("No NEO4J_PASSWORD environment variable set")

    # Define the Neo4j connection details
    uri = "neo4j+s://f0152d30.databases.neo4j.io"  # Update with your Neo4j URI if different
    user = "neo4j"  # Update with your Neo4j username if different

    # Create a Neo4j driver instance
    driver = GraphDatabase.driver(uri, auth=(user, neo4j_password))

    return driver

# Example usage
if __name__ == "__main__":
    driver = get_neo4j_connection()
    print("Connected to Neo4j database")
    driver.close()