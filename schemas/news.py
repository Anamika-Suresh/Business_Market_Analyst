from typing import List, Optional, Literal
from pydantic import BaseModel, Field, AliasChoices, ConfigDict

class NewsItem(BaseModel):
    """Specific news, funding, partnership, or corporate announcement."""
    model_config = ConfigDict(populate_by_name=True, extra="ignore")
    
    headline: str = Field(description="Headline or title of the announcement")
    summary: str = Field(default="", description="Brief summary of the development")
    category: Literal[
        "PRODUCT_LAUNCH",
        "FUNDING",
        "PARTNERSHIP",
        "ACQUISITION",
        "EXECUTIVE_CHANGE",
        "RESTRUCTURING",
        "OTHER"
    ] = Field(default="OTHER", description="Category of event")
    publication_date: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices("publication_date", "publicationDate", "date"),
        description="Date when article was published"
    )
    event_date: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices("event_date", "eventDate"),
        description="Date on which the actual event occurred"
    )
    source_url: str = Field(
        default="https://example.com/source",
        validation_alias=AliasChoices("source_url", "sourceUrl", "url", "link"),
        description="URL to the credible news source or announcement"
    )
    publisher: str = Field(default="Unknown", description="Publisher or media outlet")
    is_dated: bool = Field(default=True, description="Whether the publication date is verified")
    evidence_id: Optional[str] = Field(default=None, description="Linked evidence record ID")

class HiringSignal(BaseModel):
    """Specific hiring signal or job opening."""
    model_config = ConfigDict(populate_by_name=True, extra="ignore")
    
    role_title: str = Field(
        default="Open Position",
        validation_alias=AliasChoices("role_title", "roleTitle", "title", "role"),
        description="Title of the job opening"
    )
    department: Optional[str] = Field(default=None, description="Department, e.g. Engineering, Sales")
    location: Optional[str] = Field(default=None, description="Location or Remote status")
    date_posted: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices("date_posted", "datePosted", "date"),
        description="Date posted or observed"
    )
    source_url: str = Field(
        default="https://example.com/careers",
        validation_alias=AliasChoices("source_url", "sourceUrl", "url"),
        description="Direct URL to career portal or verified job posting"
    )
    is_active_opening: bool = Field(default=True, description="Whether position was confirmed active")
    is_stale: bool = Field(default=False, description="Whether listing is suspected of being stale/outdated")
    evidence_id: Optional[str] = Field(default=None, description="Linked evidence record ID")

class NewsAndHiring(BaseModel):
    """News and hiring intelligence produced by Agent 3."""
    model_config = ConfigDict(populate_by_name=True, extra="ignore")
    
    company_name: str = Field(
        default="Unknown",
        validation_alias=AliasChoices("company_name", "companyName", "name"),
        description="Target company analyzed"
    )
    lookback_days: int = Field(default=90, description="Configured lookback period in days")
    recent_news: List[NewsItem] = Field(
        default_factory=list,
        validation_alias=AliasChoices("recent_news", "recentNews", "news"),
        description="Recent announcements and events"
    )
    hiring_signals: List[HiringSignal] = Field(
        default_factory=list,
        validation_alias=AliasChoices("hiring_signals", "hiringSignals", "jobs"),
        description="Observed hiring signals"
    )
    hiring_trends_summary: str = Field(
        default="Standard operational recruitment signals observed within the configured review window.",
        validation_alias=AliasChoices("hiring_trends_summary", "hiringTrendsSummary", "summary"),
        description="Summary of hiring velocity and strategic focus areas"
    )
    evidence_ids: List[str] = Field(default_factory=list, description="Linked evidence record IDs")
