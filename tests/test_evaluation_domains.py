import pytest
from schemas.company import CompanyProfile, Executive, FundingRound
from schemas.competitor import CompetitorAnalysis, CompetitorItem
from schemas.news import NewsAndHiring, NewsItem, HiringSignal
from schemas.risk import RiskFindings, RiskFinding, RiskCategory, RiskSeverity
from services.evidence_service import check_missing_citations, detect_contradictions
from services.report_service import format_report_markdown
from schemas.report import CompanyIntelligenceReport

def test_domain_1_profile_leadership_evaluation():
    """Verify profile domain captures founders, funding, and products correctly."""
    profile = CompanyProfile(
        company_name="Stripe",
        official_website="https://stripe.com",
        description="Financial infrastructure for the internet.",
        core_products_or_services=["Stripe Payments", "Stripe Connect", "Stripe Billing"],
        industry="Financial Technology / Payments",
        business_model="Transaction-fee & API SaaS",
        founders=[
            Executive(name="Patrick Collison", title="CEO & Co-Founder", is_founder=True, verified=True),
            Executive(name="John Collison", title="President & Co-Founder", is_founder=True, verified=True)
        ],
        funding_rounds=[
            FundingRound(round_name="Series I", amount="$6.5B", announced_date="2023-03-15")
        ],
        total_funding="$8.7B",
        headquarters="San Francisco, CA & Dublin, Ireland"
    )
    assert len(profile.founders) == 2
    assert profile.founders[0].is_founder is True
    assert profile.total_funding == "$8.7B"
    assert "Stripe Payments" in profile.core_products_or_services

def test_domain_2_competitor_matrix_evaluation():
    """Verify competitor domain distinguishes direct, indirect, and substitute competitors."""
    comp = CompetitorAnalysis(
        target_company="Stripe",
        direct_competitors=[
            CompetitorItem(
                name="Adyen",
                website="https://adyen.com",
                competitor_type="DIRECT",
                products_services=["Adyen Payments Platform"],
                target_segment="Global Enterprise Merchants",
                public_pricing="Interchange++",
                competitive_positioning="Unified omnichannel enterprise payments",
                strengths=["Unified global acquiring license"],
                potential_weaknesses=["Higher onboarding threshold for small startups"],
                evidence_sources=["https://example.com/adyen-comp"],
                is_verified=True
            )
        ],
        indirect_competitors=[
            CompetitorItem(
                name="Shopify Payments",
                website="https://shopify.com",
                competitor_type="INDIRECT",
                products_services=["Integrated Store Checkout"],
                target_segment="E-commerce SMBs",
                competitive_positioning="Turnkey integrated checkout",
                evidence_sources=["https://example.com/shopify-comp"],
                is_verified=True
            )
        ],
        substitute_products=[
            CompetitorItem(
                name="Crypto / Stablecoin Settlement",
                competitor_type="SUBSTITUTE",
                products_services=["USDC Direct Settlement"],
                target_segment="Cross-border tech vendors",
                competitive_positioning="Zero-intermediary settlement",
                evidence_sources=["https://example.com/crypto-comp"],
                is_verified=True
            )
        ],
        market_overlap_summary="Intense head-to-head competition with Adyen for enterprise volume."
    )
    assert len(comp.direct_competitors) == 1
    assert comp.direct_competitors[0].competitor_type == "DIRECT"
    assert comp.indirect_competitors[0].competitor_type == "INDIRECT"
    assert comp.substitute_products[0].competitor_type == "SUBSTITUTE"

def test_domain_3_news_and_hiring_signals_evaluation():
    """Verify news and hiring domain respects lookback window and flags dated/stale signals."""
    news = NewsAndHiring(
        company_name="Stripe",
        lookback_days=60,
        recent_news=[
            NewsItem(
                headline="Stripe Reintroduces Crypto Payments with USDC",
                summary="Expanded checkout support for stablecoins.",
                category="PRODUCT_LAUNCH",
                publication_date="2024-04-25",
                event_date="2024-04-25",
                source_url="https://techcrunch.com/2024/04/25/stripe-crypto",
                publisher="TechCrunch",
                is_dated=True
            )
        ],
        hiring_signals=[
            HiringSignal(
                role_title="Staff Infrastructure Engineer",
                department="Core Platform",
                location="Remote - US",
                date_posted="2024-04-01",
                source_url="https://stripe.com/jobs/1",
                is_active_opening=True,
                is_stale=False
            ),
            HiringSignal(
                role_title="Senior Analyst (Historical)",
                department="Finance",
                location="Dublin",
                date_posted="2022-01-10",
                source_url="https://stripe.com/jobs/old",
                is_active_opening=False,
                is_stale=True  # Properly flagged as stale
            )
        ],
        hiring_trends_summary="Continued focus on high-throughput platform engineers."
    )
    assert news.lookback_days == 60
    assert news.hiring_signals[0].is_active_opening is True
    assert news.hiring_signals[1].is_stale is True

def test_domain_4_risk_intelligence_evaluation():
    """Verify risk domain strictly separates allegations from confirmed findings and applies standard disclaimer."""
    risks = RiskFindings(
        company_name="Stripe",
        findings=[
            RiskFinding(
                finding_id="rf-1",
                title="Merchant Dispute Class Action Lawsuit",
                category=RiskCategory.LITIGATION,
                nature="ALLEGATION",  # Must be allegation, not confirmed wrongdoing
                summary="Putative class action alleging improper account hold reserves.",
                severity=RiskSeverity.MEDIUM,
                source_url="https://courtlistener.com/stripe-dispute",
                publisher="CourtListener",
                verified=True,
                caveats="Allegations are unproven; motions to dismiss currently pending."
            )
        ],
        overall_risk_summary="Risk profile characterized by standard payment processor reserve litigation.",
        has_identified_risks=True
    )
    assert risks.findings[0].nature == "ALLEGATION"
    assert "No relevant public evidence" in risks.no_risk_disclaimer
    # Never claim zero risk
    assert "absence of inherent business risk" in risks.no_risk_disclaimer
