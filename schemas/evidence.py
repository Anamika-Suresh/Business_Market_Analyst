from enum import Enum
from typing import Optional, Literal
from pydantic import BaseModel, Field
from datetime import datetime

class EvidenceType(str, Enum):
    OFFICIAL_WEBSITE = "OFFICIAL_WEBSITE"
    REGULATORY_FILING = "REGULATORY_FILING"
    NEWS_REPORT = "NEWS_REPORT"
    CAREER_PAGE = "CAREER_PAGE"
    COURT_RECORD = "COURT_RECORD"
    INDUSTRY_ANALYSIS = "INDUSTRY_ANALYSIS"
    OTHER = "OTHER"

class VerificationStatus(str, Enum):
    VERIFIED = "VERIFIED"       # Sufficiently supported by inspected evidence
    UNVERIFIED = "UNVERIFIED"   # Source or claim could not be adequately checked
    ANALYSIS = "ANALYSIS"       # Reasoned interpretation rather than directly reported fact

class EvidenceRecord(BaseModel):
    """Reusable atomic evidence model tracing every factual claim to a source."""
    evidence_id: str = Field(description="Unique identifier for the evidence, e.g. 'ev-1'")
    source_url: str = Field(description="Direct URL where the evidence was retrieved")
    source_title: str = Field(description="Title or headline of the source page")
    publisher: str = Field(default="Unknown", description="Publisher or domain of the source")
    published_at: Optional[str] = Field(default=None, description="ISO format date or string of publication")
    retrieved_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat(), description="Timestamp when evidence was retrieved")
    claim_text: str = Field(description="The specific factual claim or finding extracted")
    evidence_type: EvidenceType = Field(default=EvidenceType.OTHER)
    verification_status: VerificationStatus = Field(default=VerificationStatus.UNVERIFIED)
    confidence_score: float = Field(default=0.7, ge=0.0, le=1.0, description="Confidence in the accuracy of the claim (0.0 to 1.0)")
    notes: Optional[str] = Field(default=None, description="Important caveats, context or verification notes")

class ValidationIssue(BaseModel):
    """Identified issue during evidence synthesis and cross-agent validation."""
    issue_type: Literal[
        "MISSING_CITATION",
        "CONTRADICTION",
        "DUPLICATE",
        "INVALID_URL",
        "STALE_INFO",
        "UNCERTAIN_DATE"
    ]
    severity: Literal["LOW", "MEDIUM", "HIGH"]
    description: str
    affected_field: str
    context: Optional[str] = None
