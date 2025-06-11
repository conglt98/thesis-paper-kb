import os
import sys

# For Neo4j
try:
    from neo4j import GraphDatabase
except ImportError:
    print("neo4j-driver not installed. Please install with 'uv add neo4j'.")
    sys.exit(1)

# For Postgres
try:
    import psycopg2
except ImportError:
    print("psycopg2 not installed. Please install with 'uv add psycopg2-binary'.")
    sys.exit(1)


def get_env_or_default(var, default):
    return os.environ.get(var, default)


# Neo4j connection info
NEO4J_URI = get_env_or_default("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USERNAME = get_env_or_default("NEO4J_USERNAME", "neo4j")
NEO4J_PASSWORD = get_env_or_default("NEO4J_PASSWORD", "password")

# Postgres connection info
POSTGRES_HOST = get_env_or_default("POSTGRES_HOST", "localhost")
POSTGRES_PORT = int(get_env_or_default("POSTGRES_PORT", 5432))
POSTGRES_USER = get_env_or_default("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = get_env_or_default("POSTGRES_PASSWORD", "password")
POSTGRES_DATABASE = get_env_or_default("POSTGRES_DATABASE", "postgres")


def test_neo4j():
    print("Testing Neo4j connection...")
    try:
        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
        with driver.session() as session:
            result = session.run("RETURN 1 AS result")
            value = result.single()["result"]
            print(f"Neo4j connection successful! Test query result: {value}")
        driver.close()
    except Exception as e:
        print(f"Neo4j connection failed: {e}")


def test_postgres():
    print("Testing Postgres connection...")
    try:
        conn = psycopg2.connect(
            host=POSTGRES_HOST,
            port=POSTGRES_PORT,
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD,
            dbname=POSTGRES_DATABASE,
            connect_timeout=int(get_env_or_default("POSTGRES_CONNECT_TIMEOUT", 3)),
        )
        cur = conn.cursor()
        cur.execute("SELECT 1;")
        value = cur.fetchone()[0]
        print(f"Postgres connection successful! Test query result: {value}")
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Postgres connection failed: {e}")


if __name__ == "__main__":
    test_neo4j()
    print()
    test_postgres()
