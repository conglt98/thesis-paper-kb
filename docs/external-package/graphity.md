Our knowledge base will employ a knowledge graph as its core storage mechanism. This approach allows for the atomization of information into discrete entities (e.g., features, services, code modules, design decisions) and the explicit definition of relationships between them (e.g., "depends on," "implemented by," "documented in")

---
title: Installation
subtitle: How to install Graphiti
---

Requirements:

- Python 3.10 or higher
- Neo4j 5.21 or higher
- OpenAI API key (Graphiti defaults to OpenAI for LLM inference and embedding)

Optional:

- Gemini, Anthropic, or Groq API key (for alternative LLM providers)

<Note>
The simplest way to install Neo4j is via [Neo4j Desktop](https://neo4j.com/download/). It provides a user-friendly interface to manage Neo4j instances and databases.
</Note>

```
pip install graphiti-core
```

or

```
poetry add graphiti-core
```

## Alternative LLM Providers

Graphiti supports multiple LLM providers beyond OpenAI. However, Graphiti works best with LLM services that support Structured Output (such as OpenAI and Gemini).
Using other services may result in incorrect output schemas and ingestion failures. This is particularly problematic when using smaller models.


To install Graphiti with support for alternative providers, use the following package extras with Poetry:

<Note>
Note that even when using Anthropic for LLM inference, OpenAI is still required for embedding functionality. Make sure to set both `OPENAI_API_KEY` and `ANTHROPIC_API_KEY` environment variables when using Anthropic.
</Note>

```
# For Anthropic support
poetry add "graphiti-core[anthropic]"

# For Google Generative AI support
poetry add "graphiti-core[google-genai]"

# For Groq support
poetry add "graphiti-core[groq]"

# For multiple providers
poetry add "graphiti-core[anthropic,groq,google-genai]"
```

These extras automatically install the required dependencies for each provider.

## OpenAI Compatible LLM Providers

Please use the `OpenAIGenericClient` to connect to OpenAI compatible LLM providers. Graphiti makes use of OpenAI Structured Output, which is not supported by other providers.

The `OpenAIGenericClient` ensures that required schema is injected into the prompt, so that the LLM can generate valid JSON output.

<Warning>
Graphiti works best with LLM services that support Structured Output (such as OpenAI and Gemini).
Using other services may result in incorrect output schemas and ingestion failures. This is particularly problematic when using smaller models.
</Warning>

## Using Graphiti with Azure OpenAI

Graphiti supports Azure OpenAI for both LLM inference and embeddings. To use Azure OpenAI, you'll need to configure both the LLM client and embedder with your Azure OpenAI credentials:

```python
from openai import AsyncAzureOpenAI
from graphiti_core import Graphiti
from graphiti_core.llm_client import OpenAIClient
from graphiti_core.embedder.openai import OpenAIEmbedder, OpenAIEmbedderConfig
from graphiti_core.cross_encoder.openai_reranker_client import OpenAIRerankerClient

# Azure OpenAI configuration
api_key = "<your-api-key>"
api_version = "<your-api-version>"
azure_endpoint = "<your-azure-endpoint>"

# Create Azure OpenAI client for LLM
azure_openai_client = AsyncAzureOpenAI(
    api_key=api_key,
    api_version=api_version,
    azure_endpoint=azure_endpoint
)

# Initialize Graphiti with Azure OpenAI clients
graphiti = Graphiti(
    "bolt://localhost:7687",
    "neo4j",
    "password",
    llm_client=OpenAIClient(
        client=azure_openai_client
    ),
    embedder=OpenAIEmbedder(
        config=OpenAIEmbedderConfig(
            embedding_model="text-embedding-3-small"  # Use your Azure deployed embedding model name
        ),
        client=azure_openai_client
    ),
    # Optional: Configure the OpenAI cross encoder with Azure OpenAI
    cross_encoder=OpenAIRerankerClient(
        client=azure_openai_client
    )
)

# Now you can use Graphiti with Azure OpenAI
```

Make sure to replace the placeholder values with your actual Azure OpenAI credentials and specify the correct embedding model name that's deployed in your Azure OpenAI service.

## Using Graphiti with Google Gemini

To use Graphiti with Google Gemini, install the required package:

```
poetry add "graphiti-core[google-genai]"
```

<Note>
When using Google Gemini, you'll need to set the `GOOGLE_API_KEY` environment variable with your Google API key.
</Note>

Here's how to configure Graphiti with Google Gemini:

```python
import os
from graphiti_core import Graphiti
from graphiti_core.llm_client.gemini_client import GeminiClient, LLMConfig
from graphiti_core.embedder.gemini import GeminiEmbedder, GeminiEmbedderConfig

# Google API key configuration
api_key = os.environ.get("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("GOOGLE_API_KEY environment variable must be set")

# Initialize Graphiti with Gemini clients
graphiti = Graphiti(
    "bolt://localhost:7687",
    "neo4j",
    "password",
    llm_client=GeminiClient(
        config=LLMConfig(
            api_key=api_key,
            model="gemini-2.0-flash"
        )
    ),
    embedder=GeminiEmbedder(
        config=GeminiEmbedderConfig(
            api_key=api_key,
            embedding_model="embedding-001"
        )
    )
)
```

## Optional Environment Variables

In addition to the provider-specific API keys, Graphiti supports several optional environment variables:

- `USE_PARALLEL_RUNTIME`: A boolean variable that can be set to true to enable Neo4j's parallel runtime feature for several search queries. Note that this feature is not supported for Neo4j Community Edition or for smaller AuraDB instances, so it's off by default.


---
title: Quick Start
subtitle: Getting started with Graphiti
---

<Info>
For complete working examples, check out the [Graphiti Quickstart Examples](https://github.com/getzep/graphiti/tree/main/examples/quickstart) on GitHub.
</Info>

## Getting Started with Graphiti

For a comprehensive overview of Graphiti and its capabilities, check out the [Overview](overview) page.

### Required Imports

First, import the necessary libraries for working with Graphiti. If you haven't installed Graphiti yet, see the [Installation](installation) page:

```python
import asyncio
import json
import logging
import os
from datetime import datetime, timezone
from logging import INFO

from dotenv import load_dotenv

from graphiti_core import Graphiti
from graphiti_core.nodes import EpisodeType
from graphiti_core.search.search_config_recipes import NODE_HYBRID_SEARCH_RRF
```

### Configuration

<Note>
Graphiti uses OpenAI by default for LLM inference and embedding. Ensure that an `OPENAI_API_KEY` is set in your environment. Support for Anthropic and Groq LLM inferences is available, too.

Graphiti also requires Neo4j connection parameters. Set the following environment variables:
- `NEO4J_URI`: The URI of your Neo4j database (default: bolt://localhost:7687)
- `NEO4J_USER`: Your Neo4j username (default: neo4j)
- `NEO4J_PASSWORD`: Your Neo4j password

For more details on requirements and setup, see the [Installation](installation) page.
</Note>

Set up logging and environment variables for connecting to the Neo4j database:

```python
# Configure logging
logging.basicConfig(
    level=INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)
logger = logging.getLogger(__name__)

load_dotenv()

# Neo4j connection parameters
# Make sure Neo4j Desktop is running with a local DBMS started
neo4j_uri = os.environ.get('NEO4J_URI', 'bolt://localhost:7687')
neo4j_user = os.environ.get('NEO4J_USER', 'neo4j')
neo4j_password = os.environ.get('NEO4J_PASSWORD', 'password')

if not neo4j_uri or not neo4j_user or not neo4j_password:
    raise ValueError('NEO4J_URI, NEO4J_USER, and NEO4J_PASSWORD must be set')
```

### Main Function

Create an async main function to run all Graphiti operations:

```python
async def main():
    # Main function implementation will go here
    pass

if __name__ == '__main__':
    asyncio.run(main())
```

### Initialization

Connect to Neo4j and set up Graphiti indices. This is required before using other Graphiti functionality:

```python
# Initialize Graphiti with Neo4j connection
graphiti = Graphiti(neo4j_uri, neo4j_user, neo4j_password)

try:
    # Initialize the graph database with graphiti's indices. This only needs to be done once.
    await graphiti.build_indices_and_constraints()

    # Additional code will go here

finally:
    # Close the connection
    await graphiti.close()
    print('\nConnection closed')
```

### Adding Episodes

Episodes are the primary units of information in Graphiti. They can be text or structured JSON and are automatically processed to extract entities and relationships. For more detailed information on episodes and bulk loading, see the [Adding Episodes](adding-episodes) page:

```python
# Episodes list containing both text and JSON episodes
episodes = [
    {
        'content': 'Kamala Harris is the Attorney General of California. She was previously '
        'the district attorney for San Francisco.',
        'type': EpisodeType.text,
        'description': 'podcast transcript',
    },
    {
        'content': 'As AG, Harris was in office from January 3, 2011 – January 3, 2017',
        'type': EpisodeType.text,
        'description': 'podcast transcript',
    },
    {
        'content': {
            'name': 'Gavin Newsom',
            'position': 'Governor',
            'state': 'California',
            'previous_role': 'Lieutenant Governor',
            'previous_location': 'San Francisco',
        },
        'type': EpisodeType.json,
        'description': 'podcast metadata',
    },
    {
        'content': {
            'name': 'Gavin Newsom',
            'position': 'Governor',
            'term_start': 'January 7, 2019',
            'term_end': 'Present',
        },
        'type': EpisodeType.json,
        'description': 'podcast metadata',
    },
]

# Add episodes to the graph
for i, episode in enumerate(episodes):
    await graphiti.add_episode(
        name=f'Freakonomics Radio {i}',
        episode_body=episode['content']
        if isinstance(episode['content'], str)
        else json.dumps(episode['content']),
        source=episode['type'],
        source_description=episode['description'],
        reference_time=datetime.now(timezone.utc),
    )
    print(f'Added episode: Freakonomics Radio {i} ({episode["type"].value})')
```

### Basic Search

The simplest way to retrieve relationships (edges) from Graphiti is using the search method, which performs a hybrid search combining semantic similarity and BM25 text retrieval. For more details on search capabilities, see the [Searching the Graph](searching) page:

```python
# Perform a hybrid search combining semantic similarity and BM25 retrieval
print("\nSearching for: 'Who was the California Attorney General?'")
results = await graphiti.search('Who was the California Attorney General?')

# Print search results
print('\nSearch Results:')
for result in results:
    print(f'UUID: {result.uuid}')
    print(f'Fact: {result.fact}')
    if hasattr(result, 'valid_at') and result.valid_at:
        print(f'Valid from: {result.valid_at}')
    if hasattr(result, 'invalid_at') and result.invalid_at:
        print(f'Valid until: {result.invalid_at}')
    print('---')
```

### Center Node Search

For more contextually relevant results, you can use a center node to rerank search results based on their graph distance to a specific node. This is particularly useful for entity-specific queries as described in the [Searching the Graph](searching) page:

```python
# Use the top search result's UUID as the center node for reranking
if results and len(results) > 0:
    # Get the source node UUID from the top result
    center_node_uuid = results[0].source_node_uuid

    print('\nReranking search results based on graph distance:')
    print(f'Using center node UUID: {center_node_uuid}')

    reranked_results = await graphiti.search(
        'Who was the California Attorney General?', center_node_uuid=center_node_uuid
    )

    # Print reranked search results
    print('\nReranked Search Results:')
    for result in reranked_results:
        print(f'UUID: {result.uuid}')
        print(f'Fact: {result.fact}')
        if hasattr(result, 'valid_at') and result.valid_at:
            print(f'Valid from: {result.valid_at}')
        if hasattr(result, 'invalid_at') and result.invalid_at:
            print(f'Valid until: {result.invalid_at}')
        print('---')
else:
    print('No results found in the initial search to use as center node.')
```

### Node Search Using Search Recipes

Graphiti provides predefined search recipes optimized for different search scenarios. Here we use NODE_HYBRID_SEARCH_RRF for retrieving nodes directly instead of edges. For a complete list of available search recipes and reranking approaches, see the [Configurable Search Strategies](searching#configurable-search-strategies) section in the Searching documentation:

```python
# Example: Perform a node search using _search method with standard recipes
print(
    '\nPerforming node search using _search method with standard recipe NODE_HYBRID_SEARCH_RRF:'
)

# Use a predefined search configuration recipe and modify its limit
node_search_config = NODE_HYBRID_SEARCH_RRF.model_copy(deep=True)
node_search_config.limit = 5  # Limit to 5 results

# Execute the node search
node_search_results = await graphiti._search(
    query='California Governor',
    config=node_search_config,
)

# Print node search results
print('\nNode Search Results:')
for node in node_search_results.nodes:
    print(f'Node UUID: {node.uuid}')
    print(f'Node Name: {node.name}')
    node_summary = node.summary[:100] + '...' if len(node.summary) > 100 else node.summary
    print(f'Content Summary: {node_summary}')
    print(f"Node Labels: {', '.join(node.labels)}")
    print(f'Created At: {node.created_at}')
    if hasattr(node, 'attributes') and node.attributes:
        print('Attributes:')
        for key, value in node.attributes.items():
            print(f'  {key}: {value}')
    print('---')
```

### Complete Example

For a complete working example that puts all these concepts together, check out the [Graphiti Quickstart Examples](https://github.com/getzep/graphiti/tree/main/examples/quickstart) on GitHub.

## Next Steps

Now that you've learned the basics of Graphiti, you can explore more advanced features:

- [Custom Entity Types](custom-entity-types): Learn how to define and use custom entity types to better model your domain-specific knowledge
- [Communities](communities): Discover how to work with communities, which are groups of related nodes that share common attributes or relationships
- [Advanced Search Techniques](searching): Explore more sophisticated search strategies, including different reranking approaches and configurable search recipes
- [Adding Fact Triples](adding-fact-triples): Learn how to directly add fact triples to your graph for more precise knowledge representation
- [Agent Integration](agent): Discover how to integrate Graphiti with LLM agents for more powerful AI applications

<Info>
Make sure to run await statements within an [async function](https://docs.python.org/3/library/asyncio-task.html).
</Info>


---
title: Adding Episodes
subtitle: How to add data to your Graphiti graph
---
<Note>
Refer to the [Custom Entity Types](custom-entity-types) page for detailed instructions on adding user-defined ontology to your graph.
</Note>

### Adding Episodes

Episodes represent a single data ingestion event. An `episode` is itself a node, and any nodes identified while ingesting the
episode are related to the episode via `MENTIONS` edges.

Episodes enable querying for information at a point in time and understanding the provenance of nodes and their edge relationships.

Supported episode types:

- `text`: Unstructured text data
- `message`: Conversational messages of the format `speaker: message...`
- `json`: Structured data, processed distinctly from the other types

The graph below was generated using the code in the [Quick Start](quick-start). Each **podcast** is an individual episode.

![Simple Graph Visualization](https://raw.githubusercontent.com/getzep/graphiti/main/images/simple_graph.svg)

#### Adding a `text` or `message` Episode

Using the `EpisodeType.text` type:

```python
await graphiti.add_episode(
    name="tech_innovation_article",
    episode_body=(
        "MIT researchers have unveiled 'ClimateNet', an AI system capable of predicting "
        "climate patterns with unprecedented accuracy. Early tests show it can forecast "
        "major weather events up to three weeks in advance, potentially revolutionizing "
        "disaster preparedness and agricultural planning."
    ),
    source=EpisodeType.text,
    # A description of the source (e.g., "podcast", "news article")
    source_description="Technology magazine article",
    # The timestamp for when this episode occurred or was created
    reference_time=datetime(2023, 11, 15, 9, 30),
)
```

Using the `EpisodeType.message` type supports passing in multi-turn conversations in the `episode_body`.

The text should be structured in `{role/name}: {message}` pairs.

```python
await graphiti.add_episode(
    name="Customer_Support_Interaction_1",
    episode_body=(
        "Customer: Hi, I'm having trouble with my Allbirds shoes. "
        "The sole is coming off after only 2 months of use.\n"
        "Support: I'm sorry to hear that. Can you please provide your order number?"
    ),
    source=EpisodeType.message,
    source_description="Customer support chat",
    reference_time=datetime(2024, 3, 15, 14, 45),
)
```

#### Adding an Episode using structured data in JSON format

JSON documents can be arbitrarily nested. However, it's advisable to keep documents compact, as they must fit within your LLM's context window.

<Note>
  For large data imports, consider using the `add_episode_bulk` API to
  efficiently add multiple episodes at once.
</Note>

```python
product_data = {
    "id": "PROD001",
    "name": "Men's SuperLight Wool Runners",
    "color": "Dark Grey",
    "sole_color": "Medium Grey",
    "material": "Wool",
    "technology": "SuperLight Foam",
    "price": 125.00,
    "in_stock": True,
    "last_updated": "2024-03-15T10:30:00Z"
}

# Add the episode to the graph
await graphiti.add_episode(
    name="Product Update - PROD001",
    episode_body=product_data,  # Pass the Python dictionary directly
    source=EpisodeType.json,
    source_description="Allbirds product catalog update",
    reference_time=datetime.now(),
)
```

#### Loading Episodes in Bulk

Graphiti offers `add_episode_bulk` for efficient batch ingestion of episodes, significantly outperforming `add_episode` for large datasets. This method is highly recommended for bulk loading.

<Warning>
Use `add_episode_bulk` only for populating empty graphs or when edge invalidation is not required. The bulk ingestion pipeline does not perform edge invalidation operations.
</Warning>
```python
product_data = [
    {
        "id": "PROD001",
        "name": "Men's SuperLight Wool Runners",
        "color": "Dark Grey",
        "sole_color": "Medium Grey",
        "material": "Wool",
        "technology": "SuperLight Foam",
        "price": 125.00,
        "in_stock": true,
        "last_updated": "2024-03-15T10:30:00Z"
    },
    ...
    {
        "id": "PROD0100",
        "name": "Kids Wool Runner-up Mizzles",
        "color": "Natural Grey",
        "sole_color": "Orange",
        "material": "Wool",
        "technology": "Water-repellent",
        "price": 80.00,
        "in_stock": true,
        "last_updated": "2024-03-17T14:45:00Z"
    }
]

# Prepare the episodes for bulk loading

bulk_episodes = [
RawEpisode(
name=f"Product Update - {product['id']}",
content=json.dumps(product),
source=EpisodeType.json,
source_description="Allbirds product catalog update",
reference_time=datetime.now()
)
for product in product_data
]

await graphiti.add_episode_bulk(bulk_episodes)

```

```
---
title: Custom Entity Types
subtitle: Enhancing Graphiti with Custom Ontologies
---

Graphiti supports custom ontologies, allowing you to define specific types with custom attributes for the nodes in your knowledge graph. This feature enables more precise and domain-specific knowledge representation. This guide explains how to create user-defined entities to model your domain knowledge.

### Defining Custom Ontologies
You can define custom entity types as Pydantic models when adding episodes to your knowledge graph.

#### Creating Entity Types
The code below is an example of defining new entity types, Customer and Product, by extending the `BaseModel` class from Pydantic:

```python
from pydantic import BaseModel, Field

class Customer(BaseModel):
    """A customer of the service"""
    name: str | None = Field(..., description="The name of the customer")
    email: str | None = Field(..., description="The email address of the customer")
    subscription_tier: str | None  = Field(..., description="The customer's subscription level")


class Product(BaseModel):
    """A product or service offering"""
    price: float | None  = Field(..., description="The price of the product or service")
    category: str | None  = Field(..., description="The category of the product")
```

#### Adding Data with Entities
Now when you add episodes to your graph, you can pass in a dictionary of the Pydantic models you created above - this will ensure that new nodes are classified into one of the provided types (or none of the provided types) and the attributes of that type are automatically populated:

```python
entity_types = {"Customer": Customer, "Product": Product}

await client.add_episode(
            name='Message',
            episode_body="New customer John (john@example.com) signed up for premium tier and purchased our Analytics Pro product ($199.99) from the Software category." ,
            reference_time=datetime.now(),
            source_description='Support Ticket Log',
            group_id=group_id,
            entity_types=entity_types,
        )
```

#### Results
When you provide custom entity types, Graphiti will:

- Extract entities and classify them according to your defined types
- Identify and populate the provided attributes of each type

This will affect the `node.labels` and `node.attributes` fields of the extracted nodes:

```python
# Example Customer Node Attributes
{
    ...
    "labels": ["Entity","Customer"],
    "attributes": {
        "name": "John",
        "email": "john@example.com",
        "subscription_tier": "premium",
    }
}

# Example Product Node Attributes
{
    ...
    "labels": ["Entity", "Product"],
    "attributes": {
        "price": 199.99,
        "category": "Software",
    }
}
```

### Schema Evolution
Your knowledge graph's schema can evolve over time as your needs change. You can update entity types by adding new attributes to existing types without breaking existing nodes. When you add new attributes, existing nodes will preserve their original attributes while supporting the new ones for future updates. This flexible approach allows your knowledge graph to grow and adapt while maintaining backward compatibility with historical data.

For example, if you initially defined a "Customer" type with basic attributes like name and email, you could later add attributes like "loyalty_tier" or "acquisition_channel" without needing to modify or migrate existing customer nodes in your graph.

### Best Practices
When extracting attributes, maintain consistent naming conventions across related entity types and include a clear and thorough description of each attribute.

Additionally, attributes should be broken down into their smallest meaningful units rather than storing compound information.

Instead of:
```python
class Employment(BaseModel):
    """User's current employment"""
    employment: str | None = Field(..., description="Employment details")
```

Use:
```python
class Employment(BaseModel):
    """User's current employment"""
    role: str | None = Field(..., description="Job title")
    employer: str | None = Field(..., description="Employer name")
    ...
```
### Migration Guide
If you're upgrading from a previous version of Graphiti:
- You can add entity types to new episodes, even if existing episodes in the graph did not have entity types. Existing nodes will continue to work without being classified.
-  To add types to previously ingested data, you need to re-ingest it with entity types set into a new graph.


---
title: Searching the Graph
subtitle: How to retrieve information from your Graphiti graph
---

The examples below demonstrate two search approaches in the Graphiti library:

1. **Hybrid Search:**

   ```python
   await graphiti.search(query)
   ```

    Combines semantic similarity and BM25 retrieval, reranked using Reciprocal Rank Fusion.

    Example: Does a broad retrieval of facts related to Allbirds Wool Runners and Jane's purchase.

2. **Node Distance Reranking:**

   ```python
   await graphiti.search(query, focal_node_uuid)
   ```

    Extends Hybrid Search above by prioritizing results based on proximity to a specified node in the graph.

    Example: Focuses on Jane-specific information, highlighting her wool allergy.

Node Distance Reranking is particularly useful for entity-specific queries, providing more contextually relevant results. It weights facts by their closeness to the focal node, emphasizing information directly related to the entity of interest.

This dual approach allows for both broad exploration and targeted, entity-specific information retrieval from the knowledge graph.

```python
query = "Can Jane wear Allbirds Wool Runners?"
jane_node_uuid = "123e4567-e89b-12d3-a456-426614174000"

def print_facts(edges):
    print("\n".join([edge.fact for edge in edges]))

# Hybrid Search
results = await graphiti.search(query)
print_facts(results)

> The Allbirds Wool Runners are sold by Allbirds.
> Men's SuperLight Wool Runners - Dark Grey (Medium Grey Sole) has a runner silhouette.
> Jane purchased SuperLight Wool Runners.

# Hybrid Search with Node Distance Reranking
await client.search(query, jane_node_uuid)
print_facts(results)

> Jane purchased SuperLight Wool Runners.
> Jane is allergic to wool.
> The Allbirds Wool Runners are sold by Allbirds.
```

## Configurable Search Strategies
Graphiti also provides a low-level search method that is more configurable than the out-of-the-box search.
This search method can be called using `graphiti._search()` and passing in an additional config parameter of type `SearchConfig`.
`SearchConfig` contains 4 fields: one for the limit, and three more configs for each of edges, nodes, and communities.
The `graphiti._search()` method returns a `SearchResults` object containing a list of nodes, edges, and communities.

The `graphiti._search()` method is quite configurable and can be complicated to work with at first.
As such, we also have a `search_config_recipes.py` file that contains a few prebuilt `SearchConfig` recipes for common use cases.


The 15 recipes are the following:

| Search Type                          | Description                                                                 |
|--------------------------------------|-----------------------------------------------------------------------------|
| COMBINED_HYBRID_SEARCH_RRF           | Performs a hybrid search with RRF reranking over edges, nodes, and communities. |
| COMBINED_HYBRID_SEARCH_MMR           | Performs a hybrid search with MMR reranking over edges, nodes, and communities. |
| COMBINED_HYBRID_SEARCH_CROSS_ENCODER | Performs a full-text search, similarity search, and BFS with cross_encoder reranking over edges, nodes, and communities. |
| EDGE_HYBRID_SEARCH_RRF               | Performs a hybrid search over edges with RRF reranking.                      |
| EDGE_HYBRID_SEARCH_MMR               | Performs a hybrid search over edges with MMR reranking.                      |
| EDGE_HYBRID_SEARCH_NODE_DISTANCE     | Performs a hybrid search over edges with node distance reranking.            |
| EDGE_HYBRID_SEARCH_EPISODE_MENTIONS  | Performs a hybrid search over edges with episode mention reranking.          |
| EDGE_HYBRID_SEARCH_CROSS_ENCODER     | Performs a hybrid search over edges with cross encoder reranking.            |
| NODE_HYBRID_SEARCH_RRF               | Performs a hybrid search over nodes with RRF reranking.                      |
| NODE_HYBRID_SEARCH_MMR               | Performs a hybrid search over nodes with MMR reranking.                      |
| NODE_HYBRID_SEARCH_NODE_DISTANCE     | Performs a hybrid search over nodes with node distance reranking.            |
| NODE_HYBRID_SEARCH_EPISODE_MENTIONS  | Performs a hybrid search over nodes with episode mentions reranking.         |
| NODE_HYBRID_SEARCH_CROSS_ENCODER     | Performs a hybrid search over nodes with cross encoder reranking.            |
| COMMUNITY_HYBRID_SEARCH_RRF          | Performs a hybrid search over communities with RRF reranking.                |
| COMMUNITY_HYBRID_SEARCH_MMR          | Performs a hybrid search over communities with MMR reranking.                |
| COMMUNITY_HYBRID_SEARCH_CROSS_ENCODER| Performs a hybrid search over communities with cross encoder reranking.      |

## Supported Reranking Approaches

**Reciprocal Rank Fusion (RRF)** enhances search by combining results from different algorithms, like BM25 and semantic search. Each algorithm's results are ranked, converted to reciprocal scores (1/rank), and summed. This aggregated score determines the final ranking, leveraging the strengths of each method for more accurate retrieval.

**Maximal Marginal Relevance (MMR)** is a search strategy that balances relevance and diversity in results. It selects results that are both relevant to the query and diverse from already chosen ones, reducing redundancy and covering different query aspects. MMR ensures comprehensive and varied search results by iteratively choosing results that maximize relevance while minimizing similarity to previously selected results.

A **Cross-Encoder** is a model that jointly encodes a query and a result, scoring their relevance by considering their combined context. This approach often yields more accurate results compared to methods that encode query and a text separately.

Graphiti supports two cross encoders:
- `OpenAIRerankerClient` (the default) and `BGERerankerClient`. Rather than use a cross-encoder model, the `OpenAIRerankerClient` uses an OpenAI model to classify relevance and the resulting `logprobs` are used to rerank results.
- The `BGERerankerClient` uses the `BAAI/bge-reranker-v2-m3` model and requires `sentence_transformers` be installed.
