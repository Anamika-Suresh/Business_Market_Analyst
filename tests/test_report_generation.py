import tempfile
import json
from pathlib import Path

from schemas.company import CompanyProfile, Executive
from schemas.competitor import CompetitorAnalysis, CompetitorItem
from schemas.news import NewsAndHiring, NewsItem
from schemas.risk import RiskFindings, RiskFinding, RiskCategory, RiskSeverity
from schemas.evidence import EvidenceRecord
from schemas.report import CompanyIntelligenceReport
from services.report_service import format_report_markdown, save_report, slugify
from nodes.report_generator import report_generator_node
from state import GraphState
from config import config

def test_slugify():
    assert slugify("Anthropic, PBC!") == "anthropic_pbc"
    assert slugify("OpenAI / Microsoft") == "openai_microsoft"

def test_markdown_and_json_generation():
    report = CompanyIntelligenceReport(
        title="MarketMind AI: Anthropic",
        target_company="Anthropic",
        executive_summary="Anthropic is a prominent AI research firm.",
        company_overview=CompanyProfile(
            company_name="Anthropic",
            official_website="https://www.anthropic.com",
            description="Developing Claude.",
            industry="Artificial Intelligence",
            business_model="B2B API & Subscription",
            founders=[Executive(name="Dario Amodei", title="CEO", is_founder=True, verified=True)]
        ),
        competitor_landscape=CompetitorAnalysis(
            target_company="Anthropic",
            direct_competitors=[
                CompetitorItem(
                    name="OpenAI",
                    website="https://openai.com",
                    competitor_type="DIRECT",
                    products_services=["ChatGPT"],
                    target_segment="Enterprise",
                    public_pricing="$20/mo",
                    competitive_positioning="First mover",
                    evidence_sources=["https://example.com/openai"],
                    is_verified=True
                )
            ],
            market_overlap_summary="Intense LLM competition."
        ),
        recent_news_and_hiring=NewsAndHiring(
            company_name="Anthropic",
            lookback_days=90,
            recent_news=[
                NewsItem(
                    headline="Claude 3 Released",
                    summary="New model family.",
                    source_url="https://example.com/claude3",
                    publication_date="2024-03-04"
                )
            ],
            hiring_trends_summary="Expanding alignment team."
        ),
        risk_intelligence=RiskFindings(
            company_name="Anthropic",
            findings=[
                RiskFinding(
                    finding_id="rf-1",
                    title="Music Copyright Lawsuit",
                    category=RiskCategory.LITIGATION,
                    nature="ONGOING_PROCEEDING",
                    summary="Training data copyright lawsuit.",
                    severity=RiskSeverity.HIGH,
                    source_url="https://example.com/lawsuit",
                    verified=True
                )
            ],
            overall_risk_summary="IP litigation active.",
            has_identified_risks=True
        ),
        evidence_records=[
            EvidenceRecord(
                evidence_id="ev-1",
                source_url="https://example.com/claude3",
                source_title="Claude 3 Article",
                claim_text="Released Claude 3 family."
            )
        ],
        sources=["https://www.anthropic.com", "https://example.com/claude3"]
    )

    # 1. Format Markdown
    md = format_report_markdown(report)
    assert "# MarketMind AI — Company Intelligence Report: Anthropic" in md
    assert "## 1. Executive Summary" in md
    assert "## 3. Founders and Key Leadership" in md
    assert "Dario Amodei" in md
    assert "### Competitive Comparison Matrix" in md
    assert "| **[OpenAI](https://openai.com)** | DIRECT |" in md
    assert "## 9. Legal, Regulatory, Security, and Reputational Risks" in md

    # 2. Persist to temporary folder
    with tempfile.TemporaryDirectory() as tmp_dir:
        md_p, json_p, meta_p = save_report(report, output_dir=tmp_dir)
        assert md_p.exists()
        assert json_p.exists()
        assert meta_p.exists()

        # Validate JSON content
        with open(json_p, "r", encoding="utf-8") as f:
            data = json.load(f)
            assert data["target_company"] == "Anthropic"
            assert data["company_overview"]["company_name"] == "Anthropic"
            assert len(data["competitor_landscape"]["direct_competitors"]) == 1

def test_report_generator_node():
    with tempfile.TemporaryDirectory() as tmp_dir:
        config.output_dir = tmp_dir
        report = CompanyIntelligenceReport(
            title="Test",
            target_company="TestCo",
            executive_summary="Summary",
            company_overview=CompanyProfile(company_name="TestCo", official_website="https://test.com", description="Desc"),
            competitor_landscape=CompetitorAnalysis(target_company="TestCo", market_overlap_summary="Overlap"),
            recent_news_and_hiring=NewsAndHiring(company_name="TestCo", hiring_trends_summary="Hiring"),
            risk_intelligence=RiskFindings(company_name="TestCo", overall_risk_summary="Risks")
        )
        state: GraphState = {"final_report": report, "errors": []}
        res = report_generator_node(state)
        assert "run_metadata" in res
        assert "report_md" in res["run_metadata"]
        assert Path(res["run_metadata"]["report_md"]).exists()
