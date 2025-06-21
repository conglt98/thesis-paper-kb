"""
Data models for the AI-Powered Knowledge Base System.
"""

import os
from typing import Dict, List, Optional, Callable
from typing import Literal
from pydantic import BaseModel, Field, PrivateAttr


class QueryRequest(BaseModel):
    """
    Model for knowledge base query requests, including advanced configuration parameters for LightRAG.
    """

    query: str = Field(..., description="The query text")
    mode: Literal["local", "global", "hybrid", "naive", "mix", "bypass"] = Field(
        "hybrid",
        description="Specifies the retrieval mode: 'local', 'global', 'hybrid', 'naive', 'mix', 'bypass'.",
    )
    """Specifies the retrieval mode:
    - "local": Focuses on context-dependent information.
    - "global": Utilizes global knowledge.
    - "hybrid": Combines local and global retrieval methods.
    - "naive": Performs a basic search without advanced techniques.
    - "mix": Integrates knowledge graph and vector retrieval.
    """
    
    only_need_context: bool = Field(
        False,
        description="If True, only returns the retrieved context without generating a response.",
    )
    only_need_prompt: bool = Field(
        False,
        description="If True, only returns the generated prompt without producing a response.",
    )
    response_type: str = Field(
        "Multiple Paragraphs",
        description="Defines the response format. Examples: 'Multiple Paragraphs', 'Single Paragraph', 'Bullet Points'.",
    )
    stream: bool = Field(
        False, description="If True, enables streaming output for real-time responses."
    )
    top_k: int = Field(
        default_factory=lambda: int(os.getenv("TOP_K", "60")),
        description="Number of top items to retrieve. Represents entities in 'local' mode and relationships in 'global' mode.",
    )
    max_token_for_text_unit: int = Field(
        default_factory=lambda: int(os.getenv("MAX_TOKEN_TEXT_CHUNK", "4000")),
        description="Maximum number of tokens allowed for each retrieved text chunk.",
    )
    max_token_for_global_context: int = Field(
        default_factory=lambda: int(os.getenv("MAX_TOKEN_RELATION_DESC", "4000")),
        description="Maximum number of tokens allocated for relationship descriptions in global retrieval.",
    )
    max_token_for_local_context: int = Field(
        default_factory=lambda: int(os.getenv("MAX_TOKEN_ENTITY_DESC", "4000")),
        description="Maximum number of tokens allocated for entity descriptions in local retrieval.",
    )
    conversation_history: Optional[List[Dict[str, str]]] = Field(
        default_factory=list,
        description='Stores past conversation history to maintain context. Format: [{"role": "user/assistant", "content": "message"}].',
    )
    history_turns: int = Field(
        3,
        description="Number of complete conversation turns (user-assistant pairs) to consider in the response context.",
    )
    ids: Optional[List[str]] = Field(
        None, description="List of ids to filter the results."
    )
    user_prompt: Optional[str] = Field(
        None,
        description="User-provided prompt for the query. If provided, this will be used instead of the default value from prompt template.",
    )
    # model_func is not serializable, so we use a private attribute
    _model_func: Optional[Callable[..., object]] = PrivateAttr(default=None)


class QueryResponse(BaseModel):
    """
    Model for knowledge base query responses.
    """

    response: str = Field(..., description="The generated response")
    status: str = Field("success", description="Status of the query operation")
    error_message: Optional[str] = Field(
        None, description="Error message if status is 'error'"
    )


class InsertTextRequest(BaseModel):
    """
    Model for inserting text into the knowledge base.
    """

    text: str = Field(..., description="The text to insert into the knowledge base")


class InsertResponse(BaseModel):
    """
    Model for knowledge base insertion responses.
    """

    status: str = Field(
        ..., description="Status of the insertion operation (success, error)"
    )
    message: Optional[str] = Field(
        None, description="Additional details about the operation"
    )


class ScientificPaper(BaseModel):
    """
    Model representing a scientific paper.
    """

    title: str = Field(..., description="Title of the scientific paper")
    doi: Optional[str] = Field(None, description="DOI of the paper")
    authors: Optional[list] = Field(None, description="List of authors")
    abstract: Optional[str] = Field(None, description="Abstract of the paper")
    keywords: Optional[list] = Field(None, description="Keywords")
    publication_year: Optional[int] = Field(None, description="Year of publication")
    journal_or_conference: Optional[str] = Field(
        None, description="Journal or conference name"
    )
    sections: Optional[list] = Field(None, description="Sections of the paper")
    references: Optional[list] = Field(None, description="References")


class Author(BaseModel):
    name: str = Field(..., description="Author's name")
    affiliation: Optional[str] = Field(None, description="Affiliation of the author")
    email: Optional[str] = Field(None, description="Email address")


class Affiliation(BaseModel):
    name: str = Field(..., description="Affiliation name")
    address: Optional[str] = Field(None, description="Affiliation address")
