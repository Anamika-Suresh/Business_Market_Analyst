from typing import List, Optional, Literal
from pydantic import BaseModel, Field, AliasChoices, ConfigDict

class CompetitorItem(BaseModel):
    """Detailed profile of a single competitor."""
    model_config = ConfigDict(populate_by_name=True, extra="ignore")
    
    name: str = Field(description="Name of the competitor")
    website: Optional[str] = Field(default=None, description="Official competitor website URL")
    competitor_type: Literal["DIRECT", "INDIRECT", "SUBSTITUTE"] = Field(
        default="DIRECT",
        validation_alias=AliasChoices("competitor_type", "competitorType", "type"),
        description="Type of competitor"
    )
    products_services: List[str] = Field(
        default_factory=list,
        validation_alias=AliasChoices("products_services", "products", "services"),
        description="Key competitor offerings"
    )
    target_segment: str = Field(
        default="Unknown",
        validation_alias=AliasChoices("target_segment", "targetSegment"),
        description="Target customer segment"
    )
    public_pricing: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices("public_pricing", "publicPricing", "pricing"),
        description="Publicly available pricing or tier info"
    )
    competitive_positioning: str = Field(
        default="Market participant",
        validation_alias=AliasChoices("competitive_positioning", "competitivePositioning", "positioning"),
        description="Market stance and value proposition"
    )
    key_differentiators: List[str] = Field(
        default_factory=list,
        validation_alias=AliasChoices("key_differentiators", "keyDifferentiators", "differentiators"),
        description="Differentiators compared to target"
    )
    strengths: List[str] = Field(default_factory=list, description="Competitive strengths backed by evidence")
    potential_weaknesses: List[str] = Field(
        default_factory=list,
        validation_alias=AliasChoices("potential_weaknesses", "potentialWeaknesses", "weaknesses"),
        description="Identified competitive weaknesses"
    )
    evidence_sources: List[str] = Field(
        default_factory=list,
        validation_alias=AliasChoices("evidence_sources", "evidenceSources", "sources"),
        description="Source URLs verifying this competitor"
    )
    is_verified: bool = Field(default=False, description="Whether this competitor profile is supported by evidence")

class CompetitorAnalysis(BaseModel):
    """Aggregated competitive intelligence report produced by Agent 2."""
    model_config = ConfigDict(populate_by_name=True, extra="ignore")
    
    target_company: str = Field(
        default="Target Company",
        validation_alias=AliasChoices("target_company", "targetCompany", "company_name", "company"),
        description="Target company analyzed"
    )
    direct_competitors: List[CompetitorItem] = Field(
        default_factory=list,
        validation_alias=AliasChoices("direct_competitors", "directCompetitors", "competitors"),
        description="Direct head-to-head competitors"
    )
    indirect_competitors: List[CompetitorItem] = Field(
        default_factory=list,
        validation_alias=AliasChoices("indirect_competitors", "indirectCompetitors"),
        description="Adjacent or indirect competitors"
    )
    substitute_products: List[CompetitorItem] = Field(
        default_factory=list,
        validation_alias=AliasChoices("substitute_products", "substituteProducts", "substitutes"),
        description="Alternative solutions/substitutes"
    )
    market_overlap_summary: str = Field(
        default="Competitive analysis based on public market positioning and segment overlap.",
        validation_alias=AliasChoices("market_overlap_summary", "marketOverlapSummary", "summary"),
        description="Synthesis of overlaps and competitive dynamics"
    )
    evidence_ids: List[str] = Field(default_factory=list, description="Linked evidence record IDs")
