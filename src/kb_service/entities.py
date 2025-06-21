from pydantic import BaseModel, Field

# --- Scientific Paper Entities ---


class ScientificPaper(BaseModel):
    """
    Represents a scientific paper or publication.
    """

    title: str = Field(..., description="The title of the scientific paper.")
    abstract: str = Field(..., description="The abstract or summary of the paper.")
    publication_year: int = Field(..., description="The year the paper was published.")
    doi: str = Field(
        ..., description="The Digital Object Identifier (DOI) of the paper."
    )
    authors: list[str] = Field(
        ..., description="List of author names (link to Author nodes)."
    )
    affiliations: list[str] = Field(
        ...,
        description="List of affiliations for the authors (link to Affiliation nodes).",
    )
    keywords: list[str] = Field(
        ..., description="List of keywords describing the paper's topics."
    )
    research_fields: list[str] = Field(
        ..., description="List of research fields or domains relevant to the paper."
    )
    sections: list[str] = Field(
        ...,
        description="List of section titles in the paper (link to PaperSection nodes).",
    )
    references: list[str] = Field(
        ...,
        description="List of DOIs or titles of referenced papers (link to Reference nodes).",
    )
    conference_or_journal: str = Field(
        ...,
        description="The name of the conference or journal where the paper was published.",
    )


class Author(BaseModel):
    """
    Represents an author of a scientific paper.
    """

    name: str = Field(..., description="Full name of the author.")
    affiliation: str = Field(
        ..., description="Affiliation of the author (link to Affiliation node)."
    )
    orcid: str = Field(..., description="ORCID identifier for the author.")


class Affiliation(BaseModel):
    """
    Represents an institution or organization affiliated with an author.
    """

    name: str = Field(..., description="Name of the institution or organization.")
    address: str = Field(..., description="Address of the institution.")


class PaperSection(BaseModel):
    """
    Represents a section within a scientific paper (e.g., Introduction, Methods, Results).
    """

    section_title: str = Field(..., description="Title of the section.")
    content: str = Field(..., description="Text content of the section.")


class Citation(BaseModel):
    """
    Represents a citation made by a scientific paper to another work.
    """

    cited_paper_doi: str = Field(..., description="DOI of the cited paper.")
    context: str = Field(
        ..., description="Textual context in which the citation appears."
    )


class Reference(BaseModel):
    """
    Represents a reference entry in a scientific paper's bibliography.
    """

    title: str = Field(..., description="Title of the referenced work.")
    authors: list[str] = Field(
        ..., description="List of authors of the referenced work."
    )
    doi: str = Field(..., description="DOI of the referenced work.")
    publication_year: int = Field(..., description="Year of publication.")


class Keyword(BaseModel):
    """
    Represents a keyword or topic associated with a scientific paper.
    """

    keyword: str = Field(..., description="The keyword or topic.")


class ResearchField(BaseModel):
    """
    Represents a research field or domain relevant to a scientific paper.
    """

    field_name: str = Field(..., description="Name of the research field.")
    description: str = Field(..., description="Description of the research field.")


class ConferenceOrJournal(BaseModel):
    """
    Represents a conference or journal where a scientific paper is published.
    """

    name: str = Field(..., description="Name of the conference or journal.")
    issn_or_isbn: str = Field(..., description="ISSN or ISBN identifier.")
    publisher: str = Field(..., description="Publisher of the conference or journal.")
