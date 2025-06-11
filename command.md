# RUN lightrag server
```
uv run lightrag-server
```

# RUn agent

```
export PYTHONPATH=.
source .env
uv run adk web src/agents
```


# Query Neo4j
## List

```
MATCH (n)
WHERE NOT (n:Episodic) // This filters out any node with the label 'Episodic'
RETURN n
LIMIT 2000
```

## Delete All Nodes and Relationships (A complete reset)

```
MATCH (n)
DETACH DELETE n
```