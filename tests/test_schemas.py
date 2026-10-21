import pytest
from pydantic import ValidationError

from schemas.company import CompanyProfile, Executive, FundingRound, CompanyMilestone
from schemas.competitor import CompetitorAnalysis, CompetitorItem
from schemas.news import NewsAndHiring, NewsItem, HiringSignal
from schemas.risk import RiskFindings, RiskFinding, RiskSeverity, RiskCategory
from schemas.evidence import EvidenceRecord, EvidenceType, VerificationStatus, ValidationIssue
from schemas.report import ResearchBrief, CompanyIntelligenceReport

def test_evidence_record_validation():
    rec = EvidenceRecord(
        evidence_id="ev-123",
        source_url="https://example.com/source",
        source_title="Example Title",
        claim_text="Verified finding regarding funding round.",
        confidence_score=0.9
    )
    assert rec.evidence_id == "ev-123"
    assert rec.verification_status == VerificationStatus.UNVERIFIED
    assert rec.confidence_score == 0.9

    # Score bounds test
    with pytest.raises(ValidationError):
        EvidenceRecord(
            evidence_id="ev-err",
            source_url="https://example.com",
            source_title="Title",
            claim_text="Claim",
            confidence_score=1.5  # Invalid > 1.0
        )

def test_company_profile_schema():
    profile = CompanyProfile(
        company_name="Acme Corp",
        official_website="https://acme.com",
        description="Pioneering enterprise AI.",
        founders=[
            Executive(name="Jane Doe", title="CEO & Co-Founder", is_founder=True, verified=True)
        ],
        funding_rounds=[
            FundingRound(round_name="Series A", amount="$10M", announced_date="2023-01-15")
        ]
    )
    assert profile.company_name == "Acme Corp"
    assert len(profile.founders) == 1
    assert profile.founders[0].name == "Jane Doe"
    assert profile.funding_rounds[0].amount == "$10M"

def test_competitor_analysis_schema():
    comp = CompetitorAnalysis(
        target_company="Acme Corp",
        direct_competitors=[
            CompetitorItem(
                name="Beta Inc",
                website="https://beta.com",
                competitor_type="DIRECT",
                products_services=["Beta Cloud"],
                target_segment="Enterprise",
                competitive_positioning="Legacy leader",
                is_verified=True
            )
        ],
        market_overlap_summary="Direct rivalry in cloud computing."
    )
    assert comp.target_company == "Acme Corp"
    assert comp.direct_competitors[0].name == "Beta Inc"
    assert comp.direct_competitors[0].competitor_type == "DIRECT"

def test_news_and_hiring_schema():
    news = NewsAndHiring(
        company_name="Acme Corp",
        lookback_days=90,
        recent_news=[
            NewsItem(
                headline="Acme Launches New Product",
                summary="Expanded into European market.",
                category="PRODUCT_LAUNCH",
                source_url="https://news.com/acme",
                publication_date="2024-02-01"
            )
        ],
        hiring_signals=[
            HiringSignal(
                role_title="Senior Engineer",
                source_url="https://acme.com/jobs/123",
                is_active_opening=True
            )
        ],
        hiring_trends_summary="Accelerating engineering headcount."
    )
    assert news.lookback_days == 90
    assert len(news.recent_news) == 1
    assert news.hiring_signals[0].is_active_opening is True

def test_risk_findings_schema():
    rf = RiskFindings(
        company_name="Acme Corp",
        findings=[
            RiskFinding(
                finding_id="rf-1",
                title="Patent Litigation",
                category=RiskCategory.LITIGATION,
                nature="ONGOING_PROCEEDING",
                summary="Pending patent dispute in district court.",
                severity=RiskSeverity.MEDIUM,
                source_url="https://courtlistener.com/case/123",
                verified=True
            )
        ],
        overall_risk_summary="Moderate litigation risk.",
        has_identified_risks=True
    )
    assert rf.has_identified_risks is True
    assert rf.findings[0].category == RiskCategory.LITIGATION
    assert "No relevant public evidence" in rf.no_risk_disclaimer
