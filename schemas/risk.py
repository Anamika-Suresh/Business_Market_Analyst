from enum import Enum
from typing import List, Optional, Literal
from pydantic import BaseModel, Field, AliasChoices, ConfigDict

class RiskSeverity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class RiskCategory(str, Enum):
    LITIGATION = "LITIGATION"
    REGULATORY = "REGULATORY"
    SECURITY_BREACH = "SECURITY_BREACH"
    CUSTOMER_COMPLAINT = "CUSTOMER_COMPLAINT"
    FINANCIAL_DISTRESS = "FINANCIAL_DISTRESS"
    REPUTATIONAL = "REPUTATIONAL"
    COMPLIANCE = "COMPLIANCE"

class RiskFinding(BaseModel):
    """Specific risk signal backed by credible public sources."""
    model_config = ConfigDict(populate_by_name=True, extra="ignore")
    
    finding_id: str = Field(default="risk-1", description="Unique ID for finding, e.g. 'risk-1'")
    title: str = Field(description="Concise description of the risk issue")
    category: RiskCategory = Field(default=RiskCategory.REPUTATIONAL, description="Category of the risk")
    nature: Literal[
        "ALLEGATION",
        "ONGOING_PROCEEDING",
        "SETTLEMENT",
        "CONFIRMED_FINDING",
        "OPINION"
    ] = Field(default="ALLEGATION", description="Legal/factual status of the risk")
    summary: str = Field(default="", description="Factual context and summary")
    severity: RiskSeverity = Field(default=RiskSeverity.MEDIUM)
    incident_date: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices("incident_date", "incidentDate", "date"),
        description="Date of occurrence or public disclosure"
    )
    source_url: str = Field(
        default="https://example.com/source",
        validation_alias=AliasChoices("source_url", "sourceUrl", "url"),
        description="Authoritative source URL (court record, regulator, major press)"
    )
    publisher: str = Field(default="Unknown", description="Source publication")
    verified: bool = Field(default=False, description="Whether corroborated by authoritative evidence")
    caveats: Optional[str] = Field(default=None, description="Important nuances, company response, or limitations")
    evidence_id: Optional[str] = Field(default=None, description="Linked evidence record ID")

class RiskFindings(BaseModel):
    """Aggregated risk intelligence produced by Agent 4."""
    model_config = ConfigDict(populate_by_name=True, extra="ignore")
    
    company_name: str = Field(
        default="Unknown",
        validation_alias=AliasChoices("company_name", "companyName", "name"),
        description="Target company analyzed"
    )
    findings: List[RiskFinding] = Field(default_factory=list, description="List of identified risk findings")
    overall_risk_summary: str = Field(
        default="Risk intelligence assessment conducted across legal, regulatory, and operational public disclosures.",
        validation_alias=AliasChoices("overall_risk_summary", "overallRiskSummary", "summary"),
        description="Synthesis of overall risk posture"
    )
    has_identified_risks: bool = Field(default=False, description="True if any credible risks were identified")
    no_risk_disclaimer: str = Field(
        default="No relevant public evidence of legal, regulatory, or severe reputational risks was identified within the sources and period reviewed. This assessment reflects only publicly verifiable information and should not be construed as an absence of inherent business risk.",
        description="Standard disclaimer ensuring no unfounded claims of absolute zero risk"
    )
    evidence_ids: List[str] = Field(default_factory=list, description="Linked evidence record IDs")
