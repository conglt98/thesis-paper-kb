# LightRAG Server and WebUI

The LightRAG Server is designed to provide a Web UI and API support. The Web UI facilitates document indexing, knowledge graph exploration, and a simple RAG query interface. LightRAG Server also provides an Ollama-compatible interface, aiming to emulate LightRAG as an Ollama chat model. This allows AI chat bots, such as Open WebUI, to access LightRAG easily.

![image-20250323122538997](./README.assets/image-20250323122538997.png)

![image-20250323122754387](./README.assets/image-20250323122754387.png)

![image-20250323123011220](./README.assets/image-20250323123011220.png)

## Getting Started

### Installation

*   Install from PyPI

```bash
pip install "lightrag-hku[api]"
```

*   Installation from Source

```bash
# Clone the repository
git clone https://github.com/HKUDS/lightrag.git

# Change to the repository directory
cd lightrag

# create a Python virtual environment if necessary
# Install in editable mode with API support
pip install -e ".[api]"
```

### Before Starting LightRAG Server

LightRAG necessitates the integration of both an LLM (Large Language Model) and an Embedding Model to effectively execute document indexing and querying operations. Prior to the initial deployment of the LightRAG server, it is essential to configure the settings for both the LLM and the Embedding Model. LightRAG supports binding to various LLM/Embedding backends:

*   ollama
*   lollms
*   openai or openai compatible
*   azure_openai

It is recommended to use environment variables to configure the LightRAG Server. There is an example environment variable file named `env.example` in the root directory of the project. Please copy this file to the startup directory and rename it to `.env`. After that, you can modify the parameters related to the LLM and Embedding models in the `.env` file. It is important to note that the LightRAG Server will load the environment variables from `.env` into the system environment variables each time it starts. Since the LightRAG Server will prioritize the settings in the system environment variables, if you modify the `.env` file after starting the LightRAG Server via the command line, you need to execute `source .env` to make the new settings take effect.

Here are some examples of common settings for LLM and Embedding models:

*   OpenAI LLM + Ollama Embedding:

```
LLM_BINDING=openai
LLM_MODEL=gpt-4o
LLM_BINDING_HOST=https://api.openai.com/v1
LLM_BINDING_API_KEY=your_api_key
### Max tokens sent to LLM (less than model context size)
MAX_TOKENS=32768

EMBEDDING_BINDING=ollama
EMBEDDING_BINDING_HOST=http://localhost:11434
EMBEDDING_MODEL=bge-m3:latest
EMBEDDING_DIM=1024
# EMBEDDING_BINDING_API_KEY=your_api_key
```

*   Ollama LLM + Ollama Embedding:

```
LLM_BINDING=ollama
LLM_MODEL=mistral-nemo:latest
LLM_BINDING_HOST=http://localhost:11434
# LLM_BINDING_API_KEY=your_api_key
### Max tokens sent to LLM (based on your Ollama Server capacity)
MAX_TOKENS=8192

EMBEDDING_BINDING=ollama
EMBEDDING_BINDING_HOST=http://localhost:11434
EMBEDDING_MODEL=bge-m3:latest
EMBEDDING_DIM=1024
# EMBEDDING_BINDING_API_KEY=your_api_key
```

### Starting LightRAG Server

The LightRAG Server supports two operational modes:
*   The simple and efficient Uvicorn mode:

```
lightrag-server
```
*   The multiprocess Gunicorn + Uvicorn mode (production mode, not supported on Windows environments):

```
lightrag-gunicorn --workers 4
```
The `.env` file **must be placed in the startup directory**.

Upon launching, the LightRAG Server will create a documents directory (default is `./inputs`) and a data directory (default is `./rag_storage`). This allows you to initiate multiple instances of LightRAG Server from different directories, with each instance configured to listen on a distinct network port.

Here are some commonly used startup parameters:

-   `--host`: Server listening address (default: 0.0.0.0)
-   `--port`: Server listening port (default: 9621)
-   `--timeout`: LLM request timeout (default: 150 seconds)
-   `--log-level`: Logging level (default: INFO)
-   `--input-dir`: Specifying the directory to scan for documents (default: ./inputs)

> The requirement for the .env file to be in the startup directory is intentionally designed this way. The purpose is to support users in launching multiple LightRAG instances simultaneously, allowing different .env files for different instances.

> **After changing the .env file, you need to open a new terminal to make  the new settings take effect.** This because the LightRAG Server will load the environment variables from .env into the system environment variables each time it starts, and LightRAG Server will prioritize the settings in the system environment variables.

### Auto scan on startup

When starting any of the servers with the `--auto-scan-at-startup` parameter, the system will automatically:

1.  Scan for new files in the input directory
2.  Index new documents that aren't already in the database
3.  Make all content immediately available for RAG queries

> The `--input-dir` parameter specifies the input directory to scan. You can trigger the input directory scan from the Web UI.

### Multiple workers for Gunicorn + Uvicorn

The LightRAG Server can operate in the `Gunicorn + Uvicorn` preload mode. Gunicorn's multiple worker (multiprocess) capability prevents document indexing tasks from blocking RAG queries. Using CPU-exhaustive document extraction tools, such as docling, can lead to the entire system being blocked in pure Uvicorn mode.

Though LightRAG Server uses one worker to process the document indexing pipeline, with the async task support of Uvicorn, multiple files can be processed in parallel. The bottleneck of document indexing speed mainly lies with the LLM. If your LLM supports high concurrency, you can accelerate document indexing by increasing the concurrency level of the LLM. Below are several environment variables related to concurrent processing, along with their default values:

```
### Number of worker processes, not greater than (2 x number_of_cores) + 1
WORKERS=2
### Number of parallel files to process in one batch
MAX_PARALLEL_INSERT=2
### Max concurrent requests to the LLM
MAX_ASYNC=4
```

### Install LightRAG as a Linux Service

Create your service file `lightrag.service` from the sample file: `lightrag.service.example`. Modify the `WorkingDirectory` and `ExecStart` in the service file:

```text
Description=LightRAG Ollama Service
WorkingDirectory=<lightrag installed directory>
ExecStart=<lightrag installed directory>/lightrag/api/lightrag-api
```

Modify your service startup script: `lightrag-api`. Change your Python virtual environment activation command as needed:

```shell
#!/bin/bash

# your python virtual environment activation
source /home/netman/lightrag-xyj/venv/bin/activate
# start lightrag api server
lightrag-server
```

Install LightRAG service. If your system is Ubuntu, the following commands will work:

```shell
sudo cp lightrag.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl start lightrag.service
sudo systemctl status lightrag.service
sudo systemctl enable lightrag.service
```

## Ollama Emulation

We provide Ollama-compatible interfaces for LightRAG, aiming to emulate LightRAG as an Ollama chat model. This allows AI chat frontends supporting Ollama, such as Open WebUI, to access LightRAG easily.

### Connect Open WebUI to LightRAG

After starting the lightrag-server, you can add an Ollama-type connection in the Open WebUI admin panel. And then a model named `lightrag:latest` will appear in Open WebUI's model management interface. Users can then send queries to LightRAG through the chat interface. You should install LightRAG as a service for this use case.

Open WebUI uses an LLM to do the session title and session keyword generation task. So the Ollama chat completion API detects and forwards OpenWebUI session-related requests directly to the underlying LLM. Screenshot from Open WebUI:

![image-20250323194750379](./README.assets/image-20250323194750379.png)

### Choose Query mode in chat

The default query mode is `hybrid` if you send a message (query) from the Ollama interface of LightRAG. You can select query mode by sending a message with a query prefix.

A query prefix in the query string can determine which LightRAG query mode is used to generate the response for the query. The supported prefixes include:

```
/local
/global
/hybrid
/naive
/mix

/bypass
/context
/localcontext
/globalcontext
/hybridcontext
/naivecontext
/mixcontext
```

For example, the chat message `/mix What's LightRAG?` will trigger a mix mode query for LightRAG. A chat message without a query prefix will trigger a hybrid mode query by default.

`/bypass` is not a LightRAG query mode; it will tell the API Server to pass the query directly to the underlying LLM, including the chat history. So the user can use the LLM to answer questions based on the chat history. If you are using Open WebUI as a front end, you can just switch the model to a normal LLM instead of using the `/bypass` prefix.

`/context` is also not a LightRAG query mode; it will tell LightRAG to return only the context information prepared for the LLM. You can check the context if it's what you want, or process the context by yourself.

## API Key and Authentication

By default, the LightRAG Server can be accessed without any authentication. We can configure the server with an API Key or account credentials to secure it.

*   API Key:

```
LIGHTRAG_API_KEY=your-secure-api-key-here
WHITELIST_PATHS=/health,/api/*
```

> Health check and Ollama emulation endpoints are excluded from API Key check by default.

*   Account credentials (the Web UI requires login before access can be granted):

LightRAG API Server implements JWT-based authentication using the HS256 algorithm. To enable secure access control, the following environment variables are required:

```bash
# For jwt auth
AUTH_ACCOUNTS='admin:admin123,user1:pass456'
TOKEN_SECRET='your-key'
TOKEN_EXPIRE_HOURS=4
```

> Currently, only the configuration of an administrator account and password is supported. A comprehensive account system is yet to be developed and implemented.

If Account credentials are not configured, the Web UI will access the system as a Guest. Therefore, even if only an API Key is configured, all APIs can still be accessed through the Guest account, which remains insecure. Hence, to safeguard the API, it is necessary to configure both authentication methods simultaneously.

## For Azure OpenAI Backend

Azure OpenAI API can be created using the following commands in Azure CLI (you need to install Azure CLI first from [https://docs.microsoft.com/en-us/cli/azure/install-azure-cli](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli)):

```bash
# Change the resource group name, location, and OpenAI resource name as needed
RESOURCE_GROUP_NAME=LightRAG
LOCATION=swedencentral
RESOURCE_NAME=LightRAG-OpenAI

az login
az group create --name $RESOURCE_GROUP_NAME --location $LOCATION
az cognitiveservices account create --name $RESOURCE_NAME --resource-group $RESOURCE_GROUP_NAME  --kind OpenAI --sku S0 --location swedencentral
az cognitiveservices account deployment create --resource-group $RESOURCE_GROUP_NAME  --model-format OpenAI --name $RESOURCE_NAME --deployment-name gpt-4o --model-name gpt-4o --model-version "2024-08-06"  --sku-capacity 100 --sku-name "Standard"
az cognitiveservices account deployment create --resource-group $RESOURCE_GROUP_NAME  --model-format OpenAI --name $RESOURCE_NAME --deployment-name text-embedding-3-large --model-name text-embedding-3-large --model-version "1"  --sku-capacity 80 --sku-name "Standard"
az cognitiveservices account show --name $RESOURCE_NAME --resource-group $RESOURCE_GROUP_NAME --query "properties.endpoint"
az cognitiveservices account keys list --name $RESOURCE_NAME -g $RESOURCE_GROUP_NAME

```

The output of the last command will give you the endpoint and the key for the OpenAI API. You can use these values to set the environment variables in the `.env` file.

```
# Azure OpenAI Configuration in .env:
LLM_BINDING=azure_openai
LLM_BINDING_HOST=your-azure-endpoint
LLM_MODEL=your-model-deployment-name
LLM_BINDING_API_KEY=your-azure-api-key
### API version is optional, defaults to latest version
AZURE_OPENAI_API_VERSION=2024-08-01-preview

### If using Azure OpenAI for embeddings
EMBEDDING_BINDING=azure_openai
EMBEDDING_MODEL=your-embedding-deployment-name
```

## LightRAG Server Configuration in Detail

The API Server can be configured in three ways (highest priority first):

*   Command line arguments
*   Environment variables or .env file
*   Config.ini (Only for storage configuration)

Most of the configurations come with default settings; check out the details in the sample file: `.env.example`. Data storage configuration can also be set by config.ini. A sample file `config.ini.example` is provided for your convenience.

### LLM and Embedding Backend Supported

LightRAG supports binding to various LLM/Embedding backends:

*   ollama
*   lollms
*   openai & openai compatible
*   azure_openai

Use environment variables `LLM_BINDING` or CLI argument `--llm-binding` to select the LLM backend type. Use environment variables `EMBEDDING_BINDING` or CLI argument `--embedding-binding` to select the Embedding backend type.

### Entity Extraction Configuration
*   ENABLE_LLM_CACHE_FOR_EXTRACT: Enable LLM cache for entity extraction (default: true)

It's very common to set `ENABLE_LLM_CACHE_FOR_EXTRACT` to true for a test environment to reduce the cost of LLM calls.

### Storage Types Supported

LightRAG uses 4 types of storage for different purposes:

*   KV_STORAGE: llm response cache, text chunks, document information
*   VECTOR_STORAGE: entities vectors, relation vectors, chunks vectors
*   GRAPH_STORAGE: entity relation graph
*   DOC_STATUS_STORAGE: document indexing status

Each storage type has several implementations:

*   KV_STORAGE supported implementations:

```
JsonKVStorage    JsonFile (default)
PGKVStorage      Postgres
RedisKVStorage   Redis
MongoKVStorage   MongoDB
```

*   GRAPH_STORAGE supported implementations:

```
NetworkXStorage      NetworkX (default)
Neo4JStorage         Neo4J
PGGraphStorage       PostgreSQL with AGE plugin
```

> Testing has shown that Neo4J delivers superior performance in production environments compared to PostgreSQL with AGE plugin.

*   VECTOR_STORAGE supported implementations:

```
NanoVectorDBStorage         NanoVector (default)
PGVectorStorage             Postgres
MilvusVectorDBStorage       Milvus
ChromaVectorDBStorage       Chroma
FaissVectorDBStorage        Faiss
QdrantVectorDBStorage       Qdrant
MongoVectorDBStorage        MongoDB
```

*   DOC_STATUS_STORAGE: supported implementations:

```
JsonDocStatusStorage        JsonFile (default)
PGDocStatusStorage          Postgres
MongoDocStatusStorage       MongoDB
```

### How to Select Storage Implementation

You can select storage implementation by environment variables. You can set the following environment variables to a specific storage implementation name before the first start of the API Server:

```
LIGHTRAG_KV_STORAGE=PGKVStorage
LIGHTRAG_VECTOR_STORAGE=PGVectorStorage
LIGHTRAG_GRAPH_STORAGE=PGGraphStorage
LIGHTRAG_DOC_STATUS_STORAGE=PGDocStatusStorage
```

You cannot change storage implementation selection after adding documents to LightRAG. Data migration from one storage implementation to another is not supported yet. For further information, please read the sample env file or config.ini file.

### LightRAG API Server Command Line Options

| Parameter             | Default       | Description                                                                                                                     |
| --------------------- | ------------- | ------------------------------------------------------------------------------------------------------------------------------- |
| --host                | 0.0.0.0       | Server host                                                                                                                     |
| --port                | 9621          | Server port                                                                                                                     |
| --working-dir         | ./rag_storage | Working directory for RAG storage                                                                                               |
| --input-dir           | ./inputs      | Directory containing input documents                                                                                            |
| --max-async           | 4             | Maximum number of async operations                                                                                              |
| --max-tokens          | 32768         | Maximum token size                                                                                                              |
| --timeout             | 150           | Timeout in seconds. None for infinite timeout (not recommended)                                                                 |
| --log-level           | INFO          | Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)                                                                           |
| --verbose             | -             | Verbose debug output (True, False)                                                                                              |
| --key                 | None          | API key for authentication. Protects the LightRAG server against unauthorized access                                            |
| --ssl                 | False         | Enable HTTPS                                                                                                                    |
| --ssl-certfile        | None          | Path to SSL certificate file (required if --ssl is enabled)                                                                     |
| --ssl-keyfile         | None          | Path to SSL private key file (required if --ssl is enabled)                                                                     |
| --top-k               | 50            | Number of top-k items to retrieve; corresponds to entities in "local" mode and relationships in "global" mode.                  |
| --cosine-threshold    | 0.4           | The cosine threshold for nodes and relation retrieval, works with top-k to control the retrieval of nodes and relations.        |
| --llm-binding         | ollama        | LLM binding type (lollms, ollama, openai, openai-ollama, azure_openai)                                                          |
| --embedding-binding   | ollama        | Embedding binding type (lollms, ollama, openai, azure_openai)                                                                   |
| --auto-scan-at-startup| -             | Scan input directory for new files and start indexing                                                                           |

### .env Examples

```bash
### Server Configuration
# HOST=0.0.0.0
PORT=9621
WORKERS=2

### Settings for document indexing
ENABLE_LLM_CACHE_FOR_EXTRACT=true
SUMMARY_LANGUAGE=Chinese
MAX_PARALLEL_INSERT=2

### LLM Configuration (Use valid host. For local services installed with docker, you can use host.docker.internal)
TIMEOUT=200
TEMPERATURE=0.0
MAX_ASYNC=4
MAX_TOKENS=32768

LLM_BINDING=openai
LLM_MODEL=gpt-4o-mini
LLM_BINDING_HOST=https://api.openai.com/v1
LLM_BINDING_API_KEY=your-api-key

### Embedding Configuration (Use valid host. For local services installed with docker, you can use host.docker.internal)
EMBEDDING_MODEL=bge-m3:latest
EMBEDDING_DIM=1024
EMBEDDING_BINDING=ollama
EMBEDDING_BINDING_HOST=http://localhost:11434

### For JWT Auth
# AUTH_ACCOUNTS='admin:admin123,user1:pass456'
# TOKEN_SECRET=your-key-for-LightRAG-API-Server-xxx
# TOKEN_EXPIRE_HOURS=48

# LIGHTRAG_API_KEY=your-secure-api-key-here-123
# WHITELIST_PATHS=/api/*
# WHITELIST_PATHS=/health,/api/*

```


## API Endpoints

All servers (LoLLMs, Ollama, OpenAI and Azure OpenAI) provide the same REST API endpoints for RAG functionality. When the API Server is running, visit:

-   Swagger UI: http://localhost:9621/docs
-   ReDoc: http://localhost:9621/redoc

You can test the API endpoints using the provided curl commands or through the Swagger UI interface. Make sure to:

1.  Start the appropriate backend service (LoLLMs, Ollama, or OpenAI)
2.  Start the RAG server
3.  Upload some documents using the document management endpoints
4.  Query the system using the query endpoints
5.  Trigger document scan if new files are put into the inputs directory

### Query Endpoints:

#### POST /query
Query the RAG system with options for different search modes.

```bash
curl -X POST "http://localhost:9621/query" \
    -H "Content-Type: application/json" \
    -d '{"query": "Your question here", "mode": "hybrid"}'
```

#### POST /query/stream
Stream responses from the RAG system.

```bash
curl -X POST "http://localhost:9621/query/stream" \
    -H "Content-Type: application/json" \
    -d '{"query": "Your question here", "mode": "hybrid"}'
```

### Document Management Endpoints:

#### POST /documents/text
Insert text directly into the RAG system.

```bash
curl -X POST "http://localhost:9621/documents/text" \
    -H "Content-Type: application/json" \
    -d '{"text": "Your text content here", "description": "Optional description"}'
```

#### POST /documents/file
Upload a single file to the RAG system.

```bash
curl -X POST "http://localhost:9621/documents/file" \
    -F "file=@/path/to/your/document.txt" \
    -F "description=Optional description"
```

#### POST /documents/batch
Upload multiple files at once.

```bash
curl -X POST "http://localhost:9621/documents/batch" \
    -F "files=@/path/to/doc1.txt" \
    -F "files=@/path/to/doc2.txt"
```

#### POST /documents/scan

Trigger document scan for new files in the input directory.

```bash
curl -X POST "http://localhost:9621/documents/scan" --max-time 1800
```

> Adjust max-time according to the estimated indexing time for all new files.

#### DELETE /documents

Clear all documents from the RAG system.

```bash
curl -X DELETE "http://localhost:9621/documents"
```

### Ollama Emulation Endpoints:

#### GET /api/version

Get Ollama version information.

```bash
curl http://localhost:9621/api/version
```

#### GET /api/tags

Get available Ollama models.

```bash
curl http://localhost:9621/api/tags
```

#### POST /api/chat

Handle chat completion requests. Routes user queries through LightRAG by selecting query mode based on query prefix. Detects and forwards OpenWebUI session-related requests (for metadata generation task) directly to the underlying LLM.

```shell
curl -N -X POST http://localhost:9621/api/chat -H "Content-Type: application/json" -d \
  '{"model":"lightrag:latest","messages":[{"role":"user","content":"猪八戒是谁"}],"stream":true}'
```

> For more information about Ollama API, please visit: [Ollama API documentation](https://github.com/ollama/ollama/blob/main/docs/api.md)

#### POST /api/generate

Handle generate completion requests. For compatibility purposes, the request is not processed by LightRAG, and will be handled by the underlying LLM model.

### Utility Endpoints:

#### GET /health
Check server health and configuration.

```bash
curl "http://localhost:9621/health"
```

### This is sample file of .env

### Server Configuration
# HOST=0.0.0.0
# PORT=9621
# WORKERS=2
# CORS_ORIGINS=http://localhost:3000,http://localhost:8080
WEBUI_TITLE='Graph RAG Engine'
WEBUI_DESCRIPTION="Simple and Fast Graph Based RAG System"

### Optional SSL Configuration
# SSL=true
# SSL_CERTFILE=/path/to/cert.pem
# SSL_KEYFILE=/path/to/key.pem

### Directory Configuration (defaults to current working directory)
# WORKING_DIR=<absolute_path_for_working_dir>
# INPUT_DIR=<absolute_path_for_doc_input_dir>

### Ollama Emulating Model Tag
# OLLAMA_EMULATING_MODEL_TAG=latest

### Max nodes return from grap retrieval
# MAX_GRAPH_NODES=1000

### Logging level
# LOG_LEVEL=INFO
# VERBOSE=False
# LOG_MAX_BYTES=10485760
# LOG_BACKUP_COUNT=5
### Logfile location (defaults to current working directory)
# LOG_DIR=/path/to/log/directory

### Settings for RAG query
# HISTORY_TURNS=3
# COSINE_THRESHOLD=0.2
# TOP_K=60
# MAX_TOKEN_TEXT_CHUNK=4000
# MAX_TOKEN_RELATION_DESC=4000
# MAX_TOKEN_ENTITY_DESC=4000

### Settings for document indexing
SUMMARY_LANGUAGE=English
# CHUNK_SIZE=1200
# CHUNK_OVERLAP_SIZE=100

### Number of parallel processing documents in one patch
# MAX_PARALLEL_INSERT=2

### Max tokens for entity/relations description after merge
# MAX_TOKEN_SUMMARY=500
### Number of entities/edges to trigger LLM re-summary on merge ( at least 3 is recommented)
# FORCE_LLM_SUMMARY_ON_MERGE=6

### Num of chunks send to Embedding in single request
# EMBEDDING_BATCH_NUM=32
### Max concurrency requests for Embedding
# EMBEDDING_FUNC_MAX_ASYNC=16
# MAX_EMBED_TOKENS=8192

### LLM Configuration
### Time out in seconds for LLM, None for infinite timeout
TIMEOUT=150
### Some models like o1-mini require temperature to be set to 1
TEMPERATURE=0.5
### Max concurrency requests of LLM
MAX_ASYNC=4
### Max tokens send to LLM (less than context size of the model)
MAX_TOKENS=32768
ENABLE_LLM_CACHE=true
ENABLE_LLM_CACHE_FOR_EXTRACT=true

### Ollama example (For local services installed with docker, you can use host.docker.internal as host)
LLM_BINDING=ollama
LLM_MODEL=mistral-nemo:latest
LLM_BINDING_API_KEY=your_api_key
LLM_BINDING_HOST=http://localhost:11434

### OpenAI alike example
# LLM_BINDING=openai
# LLM_MODEL=gpt-4o
# LLM_BINDING_HOST=https://api.openai.com/v1
# LLM_BINDING_API_KEY=your_api_key
### lollms example
# LLM_BINDING=lollms
# LLM_MODEL=mistral-nemo:latest
# LLM_BINDING_HOST=http://localhost:9600
# LLM_BINDING_API_KEY=your_api_key

### Embedding Configuration (Use valid host. For local services installed with docker, you can use host.docker.internal)
EMBEDDING_MODEL=bge-m3:latest
EMBEDDING_DIM=1024
# EMBEDDING_BINDING_API_KEY=your_api_key
### ollama example
EMBEDDING_BINDING=ollama
EMBEDDING_BINDING_HOST=http://localhost:11434
### OpenAI alike example
# EMBEDDING_BINDING=openai
# LLM_BINDING_HOST=https://api.openai.com/v1
### Lollms example
# EMBEDDING_BINDING=lollms
# EMBEDDING_BINDING_HOST=http://localhost:9600

### Optional for Azure (LLM_BINDING_HOST, LLM_BINDING_API_KEY take priority)
# AZURE_OPENAI_API_VERSION=2024-08-01-preview
# AZURE_OPENAI_DEPLOYMENT=gpt-4o
# AZURE_OPENAI_API_KEY=your_api_key
# AZURE_OPENAI_ENDPOINT=https://myendpoint.openai.azure.com

# AZURE_EMBEDDING_DEPLOYMENT=text-embedding-3-large
# AZURE_EMBEDDING_API_VERSION=2023-05-15

### Data storage selection
LIGHTRAG_KV_STORAGE=JsonKVStorage
LIGHTRAG_VECTOR_STORAGE=NanoVectorDBStorage
LIGHTRAG_GRAPH_STORAGE=NetworkXStorage
LIGHTRAG_DOC_STATUS_STORAGE=JsonDocStatusStorage

### TiDB Configuration (Deprecated)
# TIDB_HOST=localhost
# TIDB_PORT=4000
# TIDB_USER=your_username
# TIDB_PASSWORD='your_password'
# TIDB_DATABASE=your_database
### separating all data from difference Lightrag instances(deprecating)
# TIDB_WORKSPACE=default

### PostgreSQL Configuration
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=your_username
POSTGRES_PASSWORD='your_password'
POSTGRES_DATABASE=your_database
### separating all data from difference Lightrag instances(deprecating)
# POSTGRES_WORKSPACE=default

### Independent AGM Configuration(not for AMG embedded in PostreSQL)
AGE_POSTGRES_DB=
AGE_POSTGRES_USER=
AGE_POSTGRES_PASSWORD=
AGE_POSTGRES_HOST=
# AGE_POSTGRES_PORT=8529

# AGE Graph Name(apply to PostgreSQL and independent AGM)
### AGE_GRAPH_NAME is precated
# AGE_GRAPH_NAME=lightrag

### Neo4j Configuration
NEO4J_URI=neo4j+s://xxxxxxxx.databases.neo4j.io
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD='your_password'

### MongoDB Configuration
MONGO_URI=mongodb://root:root@localhost:27017/
MONGO_DATABASE=LightRAG
### separating all data from difference Lightrag instances(deprecating)
# MONGODB_GRAPH=false

### Milvus Configuration
MILVUS_URI=http://localhost:19530
MILVUS_DB_NAME=lightrag
# MILVUS_USER=root
# MILVUS_PASSWORD=your_password
# MILVUS_TOKEN=your_token

### Qdrant
QDRANT_URL=http://localhost:16333
# QDRANT_API_KEY=your-api-key

### Redis
REDIS_URI=redis://localhost:6379

### For JWT Auth
# AUTH_ACCOUNTS='admin:admin123,user1:pass456'
# TOKEN_SECRET=Your-Key-For-LightRAG-API-Server
# TOKEN_EXPIRE_HOURS=48
# GUEST_TOKEN_EXPIRE_HOURS=24
# JWT_ALGORITHM=HS256

### API-Key to access LightRAG Server API
# LIGHTRAG_API_KEY=your-secure-api-key-here
# WHITELIST_PATHS=/health,/api/*
