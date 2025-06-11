import json
from datetime import date, datetime
from neo4j import GraphDatabase, Query
from neo4j.time import DateTime, Date, Time, Duration
from src.core.config import NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD


def json_converter(o):
    """A custom JSON converter to handle Neo4j's date/time objects."""
    if isinstance(o, (datetime, date, DateTime, Date, Time, Duration)):
        return str(o)
    raise TypeError(f"Object of type {o.__class__.__name__} is not JSON serializable")


def get_graph_schema() -> str:
    """
    Retrieves the schema of the Neo4j graph database.

    This tool connects to the Neo4j database and fetches a visualization
    of the entire schema, including all node labels, relationship types,
    and the properties associated with them.

    Use this tool to understand the structure of the graph before writing
    a query with execute_cypher_query. The output is a formatted string
    that describes the graph's structure.

    Returns:
        A string representation of the graph schema.
    """
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    try:
        with driver.session() as session:
            result = session.run(Query("CALL db.schema.visualization()")).single()
            if not result:
                return "Schema not found."

            nodes = result.get("nodes", [])
            relationships = result.get("relationships", [])

            schema_parts = []

            if nodes:
                schema_parts.append("Node labels and properties:")
                for node in nodes:
                    label = node.get("name")
                    properties = ", ".join(node.get("properties", []))
                    schema_parts.append(f"- {label}: ({properties})")

            if relationships:
                schema_parts.append("\nRelationship types:")
                for rel in relationships:
                    rel_type = rel[1]
                    schema_parts.append(f"- {rel_type}")

            return "\n".join(schema_parts) if schema_parts else "Schema not found."

    except Exception as e:
        return f"Error retrieving schema: {e}"
    finally:
        driver.close()


def execute_cypher_query(query: str) -> str:
    """
        Executes a read-only Cypher query against the Neo4j database.

        This tool connects to the Neo4j database using credentials from environment
        variables, executes a given Cypher query, and returns the results as a
        JSON-formatted string. It automatically handles serialization of common
        Neo4j data types like nodes, relationships, and dates/times.

        To prevent data modification, it performs a basic check to block queries
        containing keywords like CREATE, MERGE, SET, DELETE, REMOVE.

        For security and performance, properties with 'embedding' in their name
        (e.g., 'embedding', 'name_embedding') are automatically removed from the
        results before serialization.

        Args:
            query: The Cypher query to execute.

        Returns:
            A JSON string representing the query results, or an error message.

        Examples:
            # List the names and descriptions of 10 products
            execute_cypher_query("MATCH (p:Product) RETURN p.product_name, p.description LIMIT 10")

            # List all product component (When user asking list all  product component)
            execute_cypher_query("MATCH (p:ProductFeatureGroup) RETURN p.component_name, p.summary")

            # Find features whose name contains 'score'
            execute_cypher_query("MATCH (f:ProductFeature) WHERE toLower(f.feature_name) CONTAINS 'score' RETURN f.feature_name, f.summary")

            # Explore relationships between Products and Features
            execute_cypher_query("MATCH (p:Product)-[]-(f:ProductFeature) RETURN p.product_name, type(r) AS relationship, f.feature_name LIMIT 10")

            # List all features for the 'maestro' product
            execute_cypher_query("MATCH (p:Product)-[]-(f:ProductFeature) WHERE toLower(p.product_name) CONTAINS 'maestro' RETURN f.feature_name, f.summary")

        More following this label types below:
    ```python
    [
                "Product",
                "ProductFeatureGroup",
                "ProductFeature",
                "Actor",
                "BusinessContext",
                "UserGuide",
                "BusinessProcess"
                "BusinessEvent"
                "BusinessObject",
                "Service",
                "DataStore",
                "CodeModule",
                "DataTable",
                "TechStack",
                "ServiceType",
                "DataStoreType"
    ]

    ```
    """
    forbidden_keywords = ["CREATE", "SET", "DELETE", "MERGE", "REMOVE", "DROP"]
    if any(keyword in query.upper() for keyword in forbidden_keywords):
        return json.dumps({"error": "This tool only supports read-only queries."})

    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    try:
        with driver.session() as session:
            # The query is dynamic, so we suppress the type checker warning.
            # Security is handled by the keyword check above.
            result = session.run(Query(query))  # type: ignore
            records = [record.data() for record in result]

            def _remove_embeddings_recursive(obj):
                if isinstance(obj, dict):
                    return {
                        k: _remove_embeddings_recursive(v)
                        for k, v in obj.items()
                        if "embedding" not in k.lower()
                    }
                if isinstance(obj, list):
                    return [_remove_embeddings_recursive(i) for i in obj]
                return obj

            processed_records = _remove_embeddings_recursive(records)

            return json.dumps(processed_records, indent=2, default=json_converter)
    except Exception as e:
        return json.dumps({"error": f"Query failed: {e}"})
    finally:
        driver.close()
