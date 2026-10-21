from typing import List, Optional, Union, Dict, Any
from pydantic import BaseModel, Field, AliasChoices, ConfigDict, field_validator

class Executive(BaseModel):
    """Profile of a founder or key executive."""
    model_config = ConfigDict(populate_by_name=True, extra="ignore")
    name: str = Field(description="Full name of the executive")
    title: str = Field(default="Executive", description="Role or title, e.g., 'Co-Founder & CEO'")
    bio: Optional[str] = Field(default=None, description="Short background bio")
    linkedin_url: Optional[str] = Field(default=None, description="LinkedIn or public profile URL")
    is_founder: bool = Field(default=False, description="Whether this individual is a founder")
    verified: bool = Field(default=False, description="Whether this executive record was verified by credible source")

class FundingRound(BaseModel):
    """Disclosed funding round detail."""
    model_config = ConfigDict(populate_by_name=True, extra="ignore")
    round_name: str = Field(default="Funding Round", description="e.g. 'Series B', 'Seed', 'IPO'")
    amount: Optional[str] = Field(default=None, description="e.g. '$50M', 'undisclosed'")
    announced_date: Optional[str] = Field(default=None, description="Date of announcement")
    lead_investors: List[str] = Field(default_factory=list, description="Notable investors")
    source_url: Optional[str] = Field(default=None, description="Source documenting round")

class CompanyMilestone(BaseModel):
    """Important milestone or historic development."""
    model_config = ConfigDict(populate_by_name=True, extra="ignore")
    date: Optional[str] = Field(default=None, description="Date or year of milestone")
    description: str = Field(description="Description of the milestone")
    significance: Optional[str] = Field(default=None, description="Why this matters")
    source_url: Optional[str] = Field(default=None, description="Source URL")

class CompanyProfile(BaseModel):
    """Comprehensive company overview produced by Agent 1."""
    model_config = ConfigDict(populate_by_name=True, extra="ignore")
    
    company_name: str = Field(
        default="Unknown",
        validation_alias=AliasChoices("company_name", "companyName", "name"),
        description="Official name of the company"
    )
    official_website: str = Field(
        default="",
        validation_alias=AliasChoices("official_website", "website", "url"),
        description="Canonical website URL"
    )
    description: str = Field(default="Operating company.", description="Company description and core mission")
    core_products_or_services: List[str] = Field(
        default_factory=list,
        validation_alias=AliasChoices("core_products_or_services", "products", "services", "offerings"),
        description="Primary products or services offered"
    )
    industry: str = Field(default="Unknown", description="Primary industry vertical")
    business_model: str = Field(default="Unknown", description="Business model, e.g. B2B SaaS, Marketplace")
    target_customers: List[str] = Field(
        default_factory=list,
        validation_alias=AliasChoices("target_customers", "targetCustomers", "customers"),
        description="Customer segments targeted"
    )
    founders: List[Executive] = Field(default_factory=list, description="Founders and co-founders")
    key_executives: List[Executive] = Field(default_factory=list, description="Other key leadership team members")
    funding_rounds: List[FundingRound] = Field(default_factory=list, description="Disclosed funding rounds")
    total_funding: Optional[str] = Field(default=None, description="Aggregated disclosed funding amount")
    headquarters: Optional[str] = Field(default=None, description="City, State/Region, Country")
    operating_regions: List[str] = Field(default_factory=list, description="Known operating regions")
    milestones: List[CompanyMilestone] = Field(default_factory=list, description="Key company milestones")
    evidence_ids: List[str] = Field(default_factory=list, description="Associated evidence IDs")

    @field_validator("headquarters", mode="before")
    @classmethod
    def parse_headquarters(cls, v):
        if isinstance(v, dict):
            parts = [v.get("city"), v.get("state"), v.get("country")]
            return ", ".join(p for p in parts if p)
        return v
