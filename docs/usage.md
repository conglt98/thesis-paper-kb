# Usage Guide: Scientific Paper Knowledge Base

This guide explains how to use the AI-powered knowledge base system for managing scientific papers.

## Overview
- Store, retrieve, and manage scientific papers and their metadata.
- All operations are focused on scientific paper entities (title, abstract, authors, DOI, etc.).
- Supports both Markdown file storage and Graphiti knowledge graph backend.

## 1. Add a Scientific Paper
You can add a scientific paper using the Markdown module:

```python
from src.kb_service.api import KnowledgeBaseService

service = KnowledgeBaseService()
service.markdown_module.save(
    text="""# Scientific Paper: Deep Learning for NLP\n...""",
    paper_title="Deep Learning for NLP",
    doi="10.1234/dlnlp.2024.001"
)
```

## 2. List All Papers
List all scientific papers stored in the knowledge base:

```python
papers = service.markdown_module.list_papers()
print(papers)
```

## 3. Delete a Paper
Delete a paper by title and (optionally) DOI:

```python
service.markdown_module.delete(paper_title="Deep Learning for NLP", doi="10.1234/dlnlp.2024.001")
```

## 4. Supported Fields for Scientific Paper
- **title**: Title of the paper (used as directory name)
- **doi**: Digital Object Identifier (used as filename if provided)
- **abstract**: Abstract or summary
- **authors**: List of author names
- **affiliations**: List of affiliations
- **keywords**: List of keywords
- **research_fields**: List of research fields
- **sections**: List of section titles/content
- **references**: List of referenced papers
- **conference_or_journal**: Name of the conference or journal

## 5. Example: Full Paper Entry
```python
service.markdown_module.save(
    text="""
# Scientific Paper: Deep Learning for NLP

## Abstract
This paper explores the application of deep learning techniques to NLP tasks.

## Authors
- Alice Smith
- Bob Johnson

## DOI
10.1234/dlnlp.2024.001
... (other sections)
""",
    paper_title="Deep Learning for NLP",
    doi="10.1234/dlnlp.2024.001"
)
```

## 6. Running Tests
Run the provided test script to verify storage and retrieval:

```bash
python scripts/test_kb_service.py
```

---
For advanced usage (Graphiti backend, querying, etc.), see the architecture documentation or source code in `src/kb_service/`. 