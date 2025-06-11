from pydantic import BaseModel, Field
from enum import Enum


from typing import List

# --- Abstract Business Archetype Entities ---
# Bussniess Entities


class Actor(BaseModel):
    """
    Represents a person, role, or system that performs actions or participates in processes.
    This is the "who" of the business.
    """

    actor_name: str = Field(
        ...,
        description="The canonical name of the actor. E.g., 'Candidate', 'Recruiter', 'Facility Manager', 'Payroll System', 'Admin', etc.",
    )
    description: str = Field(
        ...,
        description="A clear description of this actor's role, responsibilities, and purpose within the business.",
    )
    key_responsibilities: List[str] = Field(
        ...,
        description="A list of the primary tasks or duties this actor is responsible for. E.g., ['Submitting time cards', 'Approving job assignments'].",
    )


class BusinessObject(BaseModel):
    """
    Represents a tangible "thing" or piece of information that actors create, manage, or interact with.
    This is the "what" of the business.
    """

    business_object_name: str = Field(
        ...,
        description="The canonical name of the business object. E.g., 'Time Card', 'Job Assignment', 'Candidate Profile', 'Invoice', 'Compliance Document', etc.",
    )
    description: str = Field(
        ...,
        description="A clear description of what this object represents and its purpose in the business processes.",
    )
    key_attributes: List[str] = Field(
        ...,
        description="A list of the essential data fields or attributes this object contains. E.g., For a 'Time Card': ['Hours Worked', 'Work Date', 'Status', 'Assignment ID'].",
    )


class BusinessEvent(BaseModel):
    """
    Represents a significant occurrence or action that happens at a point in time, often changing the state of a Business Object.
    This is the "when" or the "verb" of the business.
    """

    business_event_name: str = Field(
        ...,
        description="The name of the event in a 'Noun-Verb' format. E.g., 'Time Card Submitted', 'Assignment Approved', 'Candidate Profile Updated', 'Payment Processed'.",
    )
    description: str = Field(
        ...,
        description="A clear description of what happens during this event and what triggers it.",
    )
    # --- Relationships ---
    triggered_by_actors: List[str] = Field(
        ...,
        description="List of 'Actor' names that can trigger this event. E.g., ['Candidate', 'Recruiter'].",
    )
    affects_objects: List[str] = Field(
        ...,
        description="List of 'BusinessObject' names that are created, updated, or deleted by this event. E.g., ['Time Card', 'Job Assignment'].",
    )


class BusinessProcess(BaseModel):
    """
    Represents a sequence of events and actions taken by actors to achieve a specific business goal.
    This is the "how" or the "story" of the business.
    """

    business_process_name: str = Field(
        ...,
        description="The descriptive name of the end-to-end business process. E.g., 'New Candidate Onboarding', 'Weekly Payroll Cycle', 'Client Invoicing'.",
    )
    description: str = Field(
        ...,
        description="A high-level description of the process, its goal, and its start and end points.",
    )
    # --- Relationships ---
    key_stages_or_events: List[str] = Field(
        ...,
        description="An ordered list of the names of key 'BusinessEvent's or stages that make up this process. E.g., ['Candidate Applies', 'Profile Screened', 'Assignment Offered', 'Assignment Accepted'].",
    )
    involves_actors: List[str] = Field(
        ..., description="List of 'Actor' names who participate in this process."
    )
    involves_objects: List[str] = Field(
        ...,
        description="List of 'BusinessObject' names that are central to this process.",
    )


class ProductName(str, Enum):
    MAESTRO = "Maestro (Client Portal)"
    CANDIDATE_PORTAL = "Candidate Portal"
    AI_CORE_PRODUCT = "AI Core Product"
    DATA_LAKE_AND_WAREHOUSE = "Data Lake & Warehouse"


class CoreProduct(BaseModel):
    product_name: ProductName | str = Field(
        ...,
        description="The name of the product. E.g., Maestro (Client Portal), Candidate Portal, AI Core Product, etc.",
    )
    description: str = Field(
        ..., description="The high-level description and purpose of the product."
    )
    target_user: str = Field(
        ...,
        description="The primary target user of the product (e.g., 'Healthcare Candidates', 'Recruiting Managers')",
    )


class ProductComponentName(str, Enum):
    AUTHENTICATION = "Authentication"
    TIME_CARD_MANAGEMENT = "Time Card Management"
    CANDIDATE_PROFILE_MANAGEMENT = "Candidate Profile Management"
    JOBS_MANAGEMENT = "Jobs Management"
    CANDIDATES_MANAGEMENT = "Candidates Management"
    USER_ROLES_MANAGEMENT = "User Roles Management"
    CREDENTIAL_WALLETS = "Credential Wallets"
    DASHBOARD = "Dashboard"
    REPORTING = "Reporting & Analytics"
    SETTINGS = "Settings"
    CONTACT_AND_SUPPORT = "Contact & Support"
    AUTO_JOB_SUBMISSION = "Auto Job Submission"
    MATCHING_ENGINE = "Matching Engine"
    ENGAGEMENT_SCORE = "Engagement Score"
    JOB_BOARD = "Job Board"
    EXPLORE_JOBS = "Explore Jobs (Job View, Job Apply, Bookmarks Job)"
    JOB_SEARCH = "Job Search Engine"
    PROFILE_COMPLETION = "Profile Completion"
    TIME_CARD_SUBMISSION = "Time Card Submission"
    NOTIFICATIONS_CENTER = "Notifications Center"
    DATA_TRACKING = "Data Tracking"
    DATA_PIPELINE = "Data Pipeline"


class ProductComponent(BaseModel):
    """
    Represents a major functional area or component of a product.
    It groups together multiple related features.
    """

    component_name: ProductComponentName | str = Field(
        ...,
        description=(
            "The name of the product component. Represents a major functional area or component of a product. "
            "It groups together multiple related features. Usually it can be inferred from Epic Name or ticket name in Jira. "
            "Examples include: 'Authentication', 'Time Card Management', 'Candidate Profile Management', 'Jobs Management', "
            "'Candidates Management', 'User Roles Management', 'Credential Wallets', 'Dashboard', 'Reporting & Analytics', "
            "'Settings', 'Contact & Support', 'Auto Job Submission', 'Matching Engine', 'Engagement Score', 'Job Board', "
            "'Explore Jobs (Job View, Job Apply, Bookmarks Job)', 'Job Search Engine', 'Profile Completion', "
            "'Time Card Submission', 'Notifications Center', 'Data Tracking', 'Data Pipeline'."
        ),
    )
    business_value: str = Field(
        ...,
        description="The business value of the component. Why this component is needed? What problem does it solve or business benefit does it provide?",
    )
    description: str = Field(
        ...,
        description="A description of the overall functionality of this component.",
    )
    # Relationship to the parent product
    product_belong: CoreProduct | str = Field(
        ...,
        description="The name of the 'CoreProduct' this component belongs to. E.g., 'Maestro (Client Portal)', 'Candidate Portal', 'AI Core Product', etc.",
    )


class ProductFeature(BaseModel):
    feature_name: str = Field(
        ...,
        description="The specific name of the feature. E.g., 'Login with Email/Password', 'Submit Weekly Time Card'.",
    )
    description: str = Field(
        ...,
        description="The description of what this specific feature does, and it's business value.",
    )
    component_belong: ProductComponentName | str = Field(
        ...,
        description=(
            "The product component name that the feature is a part of. "
            "Examples include: 'Authentication', 'Time Card Management', 'Candidate Profile Management', 'Jobs Management', "
            "'Candidates Management', 'User Roles Management', 'Credential Wallets', 'Dashboard', 'Reporting & Analytics', "
            "'Settings', 'Contact & Support', 'Auto Job Submission', 'Matching Engine', 'Engagement Score', 'Job Board', "
            "'Explore Jobs (Job View, Job Apply, Bookmarks Job)', 'Job Search Engine', 'Profile Completion', "
            "'Time Card Submission', 'Notifications Center', 'Data Tracking', 'Data Pipeline'."
        ),
    )
    reference_link: list[str] = Field(
        ...,
        description="List of Jira tickets, Figma links, or docs that provide audibility for this feature.",
    )


class UserStory(BaseModel):
    feature_name_belong: str = Field(
        ...,
        description="The feature that the user story belongs to",
    )
    user_stories: list[str] = Field(
        ...,
        description="The user stories of the feature. As a `[User Persona]`, I want to `[Action]` so that `[Benefit/Goal]`",
    )
    acceptance_criteria: list[str] = Field(
        ...,
        description="The acceptance criteria of the user story. 1. `[Criterion 1]` 2. `[Criterion 2]` 3. `[Criterion 3]`",
    )
    business_logic: list[str] = Field(
        ...,
        description="The business logic of the feature. 1. `[Logic 1]` 2. `[Logic 2]` 3. `[Logic 3]`. E.g. `If condition X is met, then Y occurs, otherwise Z occurs.`",
    )


class UserGuide(BaseModel):
    feature_name_belong: str = Field(
        ...,
        description="The feature that the user guide belongs to",
    )
    purpose_of_feature: str = Field(
        ...,
        description="Explain to the end-user what this feature helps them achieve in simple terms",
    )
    pre_requisites: list[str] = Field(
        ...,
        description="List any conditions that must be met or actions the user needs to have taken before they can use this feature",
    )
    step_by_step_instructions: list[str] = Field(
        ...,
        description="Clear and clean step-by-step instructions on how to use this feature.",
    )
    troubleshooting: list[str] = Field(
        ...,
        description="Troubleshooting and FAQs.",
    )


# Techinal Entities


# --- Enums for controlled vocabularies ---
class ServiceType(str, Enum):
    MICROSERVICE = "Microservice"
    MONOLITHIC_APPLICATION = "Monolithic Application"
    LIBRARY = "Library"
    DATA_PIPELINE = "Data Pipeline"
    API_GATEWAY = "API Gateway"
    OTHER = "Other"


class DataStoreType(str, Enum):
    RELATIONAL_DB = "Relational Database (e.g., PostgreSQL, MySQL)"
    NOSQL_DOCUMENT_DB = "NoSQL Document Database (e.g., MongoDB)"
    NOSQL_KEY_VALUE_DB = "NoSQL Key-Value Store (e.g., Redis, DynamoDB)"
    NOSQL_COLUMNAR_DB = "NoSQL Columnar Database (e.g., Cassandra)"
    SEARCH_ENGINE = "Search Engine (e.g., Elasticsearch, OpenSearch)"
    MESSAGE_QUEUE = "Message Queue (e.g., Kafka, RabbitMQ, SQS)"
    FILE_STORAGE = "File Storage (e.g., S3, GCS)"
    CACHE = "Cache (e.g., Redis, Memcached)"
    DATA_WAREHOUSE = "Data Warehouse (e.g., Snowflake, BigQuery)"
    LAKEHOUSE = "Lakehouse (e.g., Databricks)"
    OTHER = "Other"


class TechStack(BaseModel):
    tech_stack_name: str = Field(
        ...,
        description="The canonical name of the technology, framework, or library (e.g., 'Python', 'React', 'PostgreSQL', 'Docker', 'AWS Lambda')",
    )
    category: str = Field(
        ...,
        description="A category for the technology (e.g., 'Programming Language', 'Frontend Framework', 'Database', 'Containerization', 'Cloud Service', 'Messaging System').",
    )
    description: str = Field(
        ...,
        description="A brief description of the technology and its purpose or role in the system.",
    )


class Team(str, Enum):
    FRONTEND = "Frontend Department"
    BACKEND = "Backend Department"
    AI = "AI Department"
    DELIVERY = "Delivery Department (QA, PM, BA)"
    DEVOPS = "DevOps Department"
    OTHER = "Other"


class Service(BaseModel):
    service_name: str = Field(
        ...,
        description="Unique, identifiable name for the service or application (e.g., 'user-authentication-service', 'product-catalog-api', 'reporting-engine').",
    )
    description: str = Field(
        ...,
        description="A clear description of the service's primary responsibilities and purpose within the overall system architecture.",
    )
    service_type: ServiceType | str = Field(
        ...,
        description="The architectural classification of this service (e.g., Microservice, Monolithic Application).",
    )
    owner_team: Team | str = Field(
        ...,
        description="The development team primarily responsible for maintaining this service.",
    )
    frameworks_libraries: list[str] = Field(
        ...,
        description="Key frameworks or significant libraries used (e.g., ['Spring Boot', 'Django', 'FastAPI', 'Express.js']). Link to TechStack names.",
    )
    high_level_architecture_summaries: str = Field(
        ...,
        description="A high-level summary of the architecture of this service.",
    )
    # Relationships (represented as string identifiers for now, to be resolved into graph edges)
    implementation_product_component_names: list[ProductComponentName | str] = Field(
        ...,
        description="List of product component names that this service implements or contributes to. Examples include: 'Authentication', 'Time Card Management', 'Candidate Profile Management', 'Jobs Management', "
        "'Candidates Management', 'User Roles Management', 'Credential Wallets', 'Dashboard', 'Reporting & Analytics', "
        "'Settings', 'Contact & Support', 'Auto Job Submission', 'Matching Engine', 'Engagement Score', 'Job Board', "
        "'Explore Jobs (Job View, Job Apply, Bookmarks Job)', 'Job Search Engine', 'Profile Completion', "
        "'Time Card Submission', 'Notifications Center', 'Data Tracking', 'Data Pipeline'.",
    )
    depends_on_service_names: list[str] = Field(
        ...,
        description="List of other service names this service directly depends on.",
    )
    uses_tech_stack_names: list[str] = Field(
        ...,
        description="List of 'TechStack' names utilized by this service.",
    )
    interacts_with_data_store_names: list[str] = Field(
        ...,
        description="List of 'DataStore' names this service reads from or writes to.",
    )
    repository_link: str = Field(
        ...,
        description="Link to the repository of this service.",
    )


class DataStore(BaseModel):
    data_store_name: str = Field(
        ...,
        description="A unique, descriptive name for the data store (e.g., 'customer_profiles_db', 'product_recommendation_cache', 'audit_log_queue').",
    )
    store_type: DataStoreType | str = Field(
        ...,
        description="The type of data store (e.g., Relational Database, NoSQL Document Store, Message Queue).",
    )
    storage_location: str = Field(
        ...,
        description="The location of the data store, sepecifi (e.g., 'AWS S3 bucket: s3://my-bucket/data-store', 'Google Cloud Storage: gs://my-bucket/data-store', 'Local File System: /path/to/data-store') or generic if information is not available (e.g., 'AWS S3', 'Google Cloud Storage', 'Local File System').",
    )
    tech_stack_names: list[str] = Field(
        ...,
        description="List of tech stack names utilized by this data store.",
    )
    purpose: str = Field(
        ...,
        description="The primary purpose of this data store and the type of data it holds.",
    )
    owner_service_name: str = Field(
        ...,
        description="The service that owns this data store.",
    )
    store_data_for_product_component_names: list[ProductComponentName | str] = Field(
        ...,
        description="List of product component names whose data is primarily managed by this store."
        "Examples include: 'Authentication', 'Time Card Management', 'Candidate Profile Management', 'Jobs Management', "
        "'Candidates Management', 'User Roles Management', 'Credential Wallets', 'Dashboard', 'Reporting & Analytics', "
        "'Settings', 'Contact & Support', 'Auto Job Submission', 'Matching Engine', 'Engagement Score', 'Job Board', "
        "'Explore Jobs (Job View, Job Apply, Bookmarks Job)', 'Job Search Engine', 'Profile Completion', "
        "'Time Card Submission', 'Notifications Center', 'Data Tracking', 'Data Pipeline'.",
    )


class CodeModule(BaseModel):
    code_module_name: str = Field(
        ...,
        description="Name of the specific code module, library, or significant component within a service (e.g., 'PaymentProcessor', 'UserAuthenticationHandler').",
    )
    description: str = Field(
        ...,
        description="Detailed description of the module's responsibilities and functionality.",
    )
    service_belonging_to_name: str = Field(
        ..., description="Name of the parent 'Service' this module is a part of."
    )
    key_responsibilities: list[str] = Field(
        ...,
        description="A list of the main responsibilities or functions performed by this module.",
    )
    # Relationships
    interacts_with_module_names: list[str] = Field(
        ...,
        description="Other 'CodeModule' names (within the same or different services) it interacts with.",
    )
    implements_logic_for_feature_names: list[str] = Field(
        ...,
        description="Specific 'Feature' names or parts of features this module implements.",
    )
    references: list[str] = Field(
        ...,
        description="PR links, repo links, code paths, etc. That help audit the information.",
    )


class DataTable(BaseModel):
    table_name: str = Field(
        ...,
        description="Name of the data table (e.g., 'user_profiles', 'job_listings', 'candidate_applications').",
    )
    description: str = Field(
        ...,
        description="Short description of the data table. What it stores and why it exists.",
    )
    schema_summary: str = Field(
        ...,
        description="The summary of the schema of the data table. E.g., 'Stores user profiles with fields for name, email, and phone number.'",
    )
    owner_data_store_name: str = Field(
        ...,
        description="Name of the parent 'DataStore' this data table belongs to.",
    )
