from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

from schemas.company import CompanyProfile
from schemas.competitor import CompetitorAnalysis
from schemas.news import NewsAndHiring
from schemas.risk import RiskFindings
from schemas.evidence import EvidenceRecord, ValidationIssue

class ResearchBrief(BaseModel):
    """Shared research brief constructed by Supervisor for the 4 specialist agents."""
    company_name: str = Field(description="Validated target company name")
    company_url: Optional[str] = Field(default=None, description="Validated official company URL")
    lookback_days: int = Field(default=90, description="Configured lookback period for news and signals")
    research_date: str = Field(default_factory=lambda: datetime.utcnow().strftime("%Y-%m-%d"), description="Date of research")
    focus_areas: List[str] = Field(default_factory=lambda: ["profile", "competitors", "news_hiring", "risks"])
    identified_domains: List[str] = Field(default_factory=list, description="Associated official domains/aliases")
    user_priorities: Optional[str] = Field(default=None, description="Specific research priorities requested by user")
    is_ambiguous: bool = Field(default=False, description="Flag indicating if company name requires clarification")
    clarification_message: Optional[str] = Field(default=None, description="Message to user if clarification needed")

class CompanyIntelligenceReport(BaseModel):
    """Consolidated MarketMind AI intelligence report."""
    title: str = Field(description="Report title")
    target_company: str = Field(description="Target company name")
    executive_summary: str = Field(description="High-level synthesis of findings across all dimensions")
    company_overview: CompanyProfile = Field(description="Agent 1 findings")
    competitor_landscape: CompetitorAnalysis = Field(description="Agent 2 findings")
    recent_news_and_hiring: NewsAndHiring = Field(description="Agent 3 findings")
    risk_intelligence: RiskFindings = Field(description="Agent 4 findings")
    strategic_opportunities: List[str] = Field(default_factory=list, description="Strategic insights and opportunities")
    evidence_quality_and_gaps: List[str] = Field(default_factory=list, description="Gaps, unverified items, and limitations")
    evidence_records: List[EvidenceRecord] = Field(default_factory=list, description="Traceable evidence inventory")
    validation_issues: List[ValidationIssue] = Field(default_factory=list, description="Validation issues flagged")
    sources: List[str] = Field(default_factory=list, description="Unique source URLs referenced")
    generated_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    run_metadata: Dict[str, Any] = Field(default_factory=dict, description="Execution metadata, models, and timestamps")
