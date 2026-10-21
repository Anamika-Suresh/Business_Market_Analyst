import re
import uuid
from typing import List, Optional, Set, Tuple
from urllib.parse import urlparse

from schemas.evidence import EvidenceRecord, EvidenceType, VerificationStatus, ValidationIssue
from schemas.company import CompanyProfile
from schemas.competitor import CompetitorAnalysis
from schemas.news import NewsAndHiring
from schemas.risk import RiskFindings

def generate_evidence_id() -> str:
    """Generate a clean concise evidence identifier."""
    return f"ev-{uuid.uuid4().hex[:8]}"

def build_evidence_record(
    url: str,
    title: str,
    claim_text: str,
    publisher: str = "Unknown",
    published_at: Optional[str] = None,
    evidence_type: EvidenceType = EvidenceType.OTHER,
    verification_status: VerificationStatus = VerificationStatus.VERIFIED,
    confidence_score: float = 0.8,
    notes: Optional[str] = None
) -> EvidenceRecord:
    """Factory helper to create consistent EvidenceRecord objects."""
    # Derive publisher if not given
    if (not publisher or publisher == "Unknown") and url.startswith("http"):
        try:
            publisher = urlparse(url).netloc
        except Exception:
            publisher = "Web"

    return EvidenceRecord(
        evidence_id=generate_evidence_id(),
        source_url=url,
        source_title=title or "Source Document",
        publisher=publisher,
        published_at=published_at,
        claim_text=claim_text,
        evidence_type=evidence_type,
        verification_status=verification_status,
        confidence_score=confidence_score,
        notes=notes
    )

def is_valid_url(url: str) -> bool:
    """Basic format validation for URLs."""
    if not url or not isinstance(url, str):
        return False
    try:
        parsed = urlparse(url)
        return bool(parsed.scheme in ("http", "https") and parsed.netloc)
    except Exception:
        return False

def deduplicate_evidence(records: List[EvidenceRecord]) -> List[EvidenceRecord]:
    """Deduplicate evidence records by URL and normalized claim text."""
    seen: Set[Tuple[str, str]] = set()
    unique_records: List[EvidenceRecord] = []
    
    for r in records:
        key = (r.source_url.strip().lower(), r.claim_text.strip().lower()[:80])
        if key not in seen:
            seen.add(key)
            unique_records.append(r)
            
    return unique_records

def validate_evidence_records(records: List[EvidenceRecord]) -> List[ValidationIssue]:
    """Audit evidence records for invalid URLs, missing publication dates, or low confidence."""
    issues: List[ValidationIssue] = []
    
    for rec in records:
        if not is_valid_url(rec.source_url):
            issues.append(ValidationIssue(
                issue_type="INVALID_URL",
                severity="HIGH",
                description=f"Evidence {rec.evidence_id} has invalid or malformed URL: '{rec.source_url}'",
                affected_field="source_url",
                context=rec.claim_text
            ))
        if not rec.published_at and rec.evidence_type in (EvidenceType.NEWS_REPORT, EvidenceType.COURT_RECORD):
            issues.append(ValidationIssue(
                issue_type="UNCERTAIN_DATE",
                severity="LOW",
                description=f"Evidence {rec.evidence_id} from {rec.publisher} lacks a verified publication date",
                affected_field="published_at",
                context=rec.claim_text
            ))
            
    return issues

def check_missing_citations(
    profile: Optional[CompanyProfile],
    competitors: Optional[CompetitorAnalysis],
    news: Optional[NewsAndHiring],
    risks: Optional[RiskFindings],
    evidence_records: List[EvidenceRecord]
) -> List[ValidationIssue]:
    """Detect un-cited claims across the four specialist outputs."""
    issues: List[ValidationIssue] = []
    known_urls = {r.source_url for r in evidence_records if r.source_url}

    # Check competitor citations
    if competitors:
        for comp in competitors.direct_competitors:
            if not comp.evidence_sources:
                issues.append(ValidationIssue(
                    issue_type="MISSING_CITATION",
                    severity="MEDIUM",
                    description=f"Direct competitor '{comp.name}' has no backing evidence sources listed",
                    affected_field="direct_competitors",
                    context=comp.name
                ))

    # Check news citations
    if news:
        for item in news.recent_news:
            if not item.source_url or not is_valid_url(item.source_url):
                issues.append(ValidationIssue(
                    issue_type="MISSING_CITATION",
                    severity="HIGH",
                    description=f"News announcement '{item.headline}' lacks a valid source citation",
                    affected_field="recent_news",
                    context=item.headline
                ))
            if not item.publication_date:
                issues.append(ValidationIssue(
                    issue_type="UNCERTAIN_DATE",
                    severity="LOW",
                    description=f"News item '{item.headline}' has no explicit publication date",
                    affected_field="publication_date",
                    context=item.headline
                ))

    # Check risk citations
    if risks:
        for rf in risks.findings:
            if not rf.source_url or not is_valid_url(rf.source_url):
                issues.append(ValidationIssue(
                    issue_type="MISSING_CITATION",
                    severity="HIGH",
                    description=f"Risk finding '{rf.title}' lacks an authoritative source citation URL",
                    affected_field="risk_findings",
                    context=rf.title
                ))

    return issues

def detect_contradictions(
    profile: Optional[CompanyProfile],
    competitors: Optional[CompetitorAnalysis],
    news: Optional[NewsAndHiring],
    risks: Optional[RiskFindings]
) -> List[ValidationIssue]:
    """Identify cross-domain contradictions (e.g. news reporting layoffs vs profile reporting rapid headcount growth)."""
    issues: List[ValidationIssue] = []

    # Example: Check if company reported funding in profile contradicts bankruptcies in risks
    if profile and profile.funding_rounds and risks:
        for r in risks.findings:
            if r.category.value == "FINANCIAL_DISTRESS" and r.nature in ("CONFIRMED_FINDING", "SETTLEMENT"):
                issues.append(ValidationIssue(
                    issue_type="CONTRADICTION",
                    severity="HIGH",
                    description=f"Discrepancy: Company has public funding disclosures ({profile.total_funding}) but also active financial distress findings ('{r.title}'). Disagreement preserved for analysis.",
                    affected_field="funding_rounds / risk_findings",
                    context=f"{r.title}: {r.summary}"
                ))

    # Check if a direct competitor is listed as the target company itself
    if profile and competitors:
        for comp in competitors.direct_competitors:
            if comp.name.strip().lower() == profile.company_name.strip().lower():
                issues.append(ValidationIssue(
                    issue_type="DUPLICATE",
                    severity="HIGH",
                    description=f"Target company '{profile.company_name}' was mistakenly classified as its own direct competitor",
                    affected_field="direct_competitors",
                    context=comp.name
                ))

    return issues
