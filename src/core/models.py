"""
Data models for the AI-Powered Knowledge Base System.
"""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    """
    Model for knowledge base query requests.
    """

    query: str = Field(..., description="The query text")
    mode: str = Field(
        "hybrid", description="Query mode (local, global, hybrid, naive, mix, bypass)"
    )
    only_need_context: Optional[bool] = Field(
        None,
        description="If True, only returns the retrieved context without generating a response",
    )
    only_need_prompt: Optional[bool] = Field(
        None,
        description="If True, only returns the generated prompt without producing a response",
    )
    response_type: Optional[str] = Field(
        None,
        description="Defines the response format (e.g., 'Multiple Paragraphs', 'Single Paragraph', 'Bullet Points')",
    )
    top_k: Optional[int] = Field(None, description="Number of top items to retrieve")
    conversation_history: Optional[List[Dict[str, str]]] = Field(
        None,
        description="Previous conversation turns in the format [{'role': 'user/assistant', 'content': 'message'}]",
    )


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


class FeatureUpdateRequest(BaseModel):
    """
    Model for feature update requests.
    """

    feature_name: str = Field(
        ..., description="The name of the feature to add or update"
    )
    feature_description: str = Field(..., description="The description of the feature")
    parent_node: Optional[str] = Field(
        None, description="The parent node ID in the mermaid diagram"
    )


class FeatureUpdateResponse(BaseModel):
    """
    Model for feature update responses.
    """

    status: str = Field(
        ..., description="Status of the update operation (success, error)"
    )
    message: Optional[str] = Field(
        None, description="Additional details about the operation"
    )
    updated_diagram: Optional[str] = Field(
        None, description="The updated mermaid diagram"
    )


# Custom Entity Models for Graphiti
