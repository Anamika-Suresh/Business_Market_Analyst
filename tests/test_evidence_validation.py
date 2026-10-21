from schemas.company import CompanyProfile, FundingRound
from schemas.competitor import CompetitorAnalysis, CompetitorItem
from schemas.news import NewsAndHiring, NewsItem
from schemas.risk import RiskFindings, RiskFinding, RiskCategory, RiskSeverity
from schemas.evidence import EvidenceRecord, EvidenceType, VerificationStatus
from services.evidence_service import (
    validate_evidence_records,
    check_missing_citations,
    detect_contradictions,
    deduplicate_evidence
)
from nodes.evidence_validation import evidence_validation_node
from state import GraphState

def test_evidence_deduplication():
    records = [
        EvidenceRecord(
            evidence_id="ev-1",
            source_url="https://example.com/a",
            source_title="Article A",
            claim_text="Company raised $100M in Series B round."
        ),
        EvidenceRecord(
            evidence_id="ev-2",
            source_url="https://example.com/a",  # Same URL and claim
            source_title="Article A Copy",
            claim_text="Company raised $100M in Series B round."
        ),
        EvidenceRecord(
            evidence_id="ev-3",
            source_url="https://example.com/b",
            source_title="Article B",
            claim_text="Company launched new SDK."
        ),
    ]
    unique = deduplicate_evidence(records)
    assert len(unique) == 2
    urls = [r.source_url for r in unique]
    assert "https://example.com/a" in urls
    assert "https://example.com/b" in urls

def test_missing_citation_detection():
    # Competitor without evidence source
    comp = CompetitorAnalysis(
        target_company="Acme Corp",
        direct_competitors=[
            CompetitorItem(
                name="RivalCo",
                competitive_positioning="Rival",
                evidence_sources=[]  # Missing citation!
            )
        ],
        market_overlap_summary="Overlap"
    )
    issues = check_missing_citations(None, comp, None, None, [])
    assert any(i.issue_type == "MISSING_CITATION" for i in issues)
    assert any("RivalCo" in i.description for i in issues)

def test_contradiction_detection():
    profile = CompanyProfile(
        company_name="Acme Corp",
        official_website="https://acme.com",
        description="Prospering AI leader.",
        total_funding="$500M",
        funding_rounds=[FundingRound(round_name="Series C", amount="$100M")]
    )
    risks = RiskFindings(
        company_name="Acme Corp",
        findings=[
            RiskFinding(
                finding_id="rf-1",
                title="Chapter 11 Bankruptcy Filing",
                category=RiskCategory.FINANCIAL_DISTRESS,
                nature="CONFIRMED_FINDING",
                summary="Filed for bankruptcy restructuring.",
                severity=RiskSeverity.CRITICAL,
                source_url="https://court.gov/case/acme",
                verified=True
            )
        ],
        overall_risk_summary="High distress",
        has_identified_risks=True
    )
    issues = detect_contradictions(profile, None, None, risks)
    assert any(i.issue_type == "CONTRADICTION" for i in issues)

def test_evidence_validation_node_synthesis():
    state: GraphState = {
        "company_name": "Anthropic",
        "company_profile": CompanyProfile(
            company_name="Anthropic",
            official_website="https://www.anthropic.com",
            description="Leading AI safety research lab.",
            industry="Artificial Intelligence"
        ),
        "competitor_analysis": CompetitorAnalysis(
            target_company="Anthropic",
            direct_competitors=[
                CompetitorItem(
                    name="OpenAI",
                    competitive_positioning="Market Leader",
                    evidence_sources=["https://example.com/comp"]
                )
            ],
            market_overlap_summary="Direct competition"
        ),
        "news_and_hiring": NewsAndHiring(
            company_name="Anthropic",
            lookback_days=90,
            recent_news=[
                NewsItem(
                    headline="Expansion in Europe",
                    summary="Opened Dublin office.",
                    source_url="https://example.com/news",
                    publication_date="2024-03-01"
                )
            ],
            hiring_trends_summary="Growth"
        ),
        "risk_findings": RiskFindings(
            company_name="Anthropic",
            overall_risk_summary="Low immediate regulatory sanctions",
            has_identified_risks=False
        ),
        "evidence_records": [
            EvidenceRecord(
                evidence_id="ev-1",
                source_url="https://example.com/news",
                source_title="News",
                claim_text="Opened Dublin office."
            )
        ]
    }
    result = evidence_validation_node(state)
    report = result["final_report"]
    assert report is not None
    assert report.target_company == "Anthropic"
    assert "Anthropic operates in the" in report.executive_summary
    assert len(report.sources) > 0
