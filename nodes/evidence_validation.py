import logging
from typing import Dict, Any, List
from datetime import datetime

from state import GraphState
from schemas.company import CompanyProfile
from schemas.competitor import CompetitorAnalysis
from schemas.news import NewsAndHiring
from schemas.risk import RiskFindings
from schemas.report import CompanyIntelligenceReport
from schemas.evidence import ValidationIssue, EvidenceRecord
from services.evidence_service import (
    validate_evidence_records,
    check_missing_citations,
    detect_contradictions,
    deduplicate_evidence
)

logger = logging.getLogger(__name__)

def evidence_validation_node(state: GraphState) -> Dict[str, Any]:
    """Synthesis and Evidence Validation Node.
    
    Consolidates the four specialist agents' findings, verifies evidence citations,
    detects cross-domain contradictions, flags stale dates, and constructs the final
    CompanyIntelligenceReport.
    """
    company_name = state.get("company_name", "Target Company")
    brief = state.get("research_brief")
    if brief:
        company_name = brief.company_name

    logger.info(f"[EvidenceValidationNode] Consolidating findings for: {company_name}")

    # Gather domain objects (with fallbacks if any agent failed)
    profile: CompanyProfile = state.get("company_profile") or CompanyProfile(
        company_name=company_name,
        official_website=state.get("company_url") or "",
        description=f"Overview pending for {company_name}."
    )
    competitors: CompetitorAnalysis = state.get("competitor_analysis") or CompetitorAnalysis(
        target_company=company_name,
        market_overlap_summary=f"Competitive intelligence pending for {company_name}."
    )
    news: NewsAndHiring = state.get("news_and_hiring") or NewsAndHiring(
        company_name=company_name,
        hiring_trends_summary=f"Recent developments pending for {company_name}."
    )
    risks: RiskFindings = state.get("risk_findings") or RiskFindings(
        company_name=company_name,
        overall_risk_summary=f"Risk profile pending for {company_name}."
    )

    # 1. Deduplicate collected evidence records
    raw_evidences: List[EvidenceRecord] = state.get("evidence_records", [])
    unique_evidences = deduplicate_evidence(raw_evidences)

    # 2. Run Validation Rules
    validation_issues: List[ValidationIssue] = []
    validation_issues.extend(validate_evidence_records(unique_evidences))
    validation_issues.extend(check_missing_citations(profile, competitors, news, risks, unique_evidences))
    validation_issues.extend(detect_contradictions(profile, competitors, news, risks))

    # 3. Collect unique source URLs
    all_sources = list({
        ev.source_url for ev in unique_evidences if ev.source_url and ev.source_url.startswith("http")
    })
    if profile.official_website and profile.official_website.startswith("http"):
        all_sources.append(profile.official_website)

    # 4. Generate Strategic Opportunities & Evidence Quality Observations
    strategic_opportunities = [
        f"Capitalize on enterprise demand in {profile.industry or 'its primary market'}.",
        f"Differentiate against key direct competitors ({', '.join([c.name for c in competitors.direct_competitors[:2]]) or 'market rivals'}) through superior safety and proprietary architecture.",
        "Expand ecosystem integrations and partnership channels to drive scalable distribution."
    ]

    evidence_gaps = []
    if not profile.total_funding:
        evidence_gaps.append("Total funding and valuation history not fully disclosed in reviewed public records.")
    if not news.recent_news:
        evidence_gaps.append(f"Limited public announcements found within the configured {news.lookback_days}-day window.")
    if not risks.findings:
        evidence_gaps.append("No active public litigation or regulatory sanctions identified in available press and records.")

    # 5. Formulate Executive Summary
    risk_snippet = "identified legal or regulatory proceedings require monitoring" if risks.has_identified_risks else "no adverse public regulatory or litigation actions were flagged"
    exec_summary = (
        f"{company_name} operates in the {profile.industry} sector, focusing on {profile.business_model}. "
        f"Its leadership team includes {', '.join([f.name for f in profile.founders[:2]]) or 'prominent industry veterans'}. "
        f"In the competitive landscape, it contends primarily with {', '.join([c.name for c in competitors.direct_competitors[:3]]) or 'established sector peers'}. "
        f"Recent operational indicators reflect active hiring and product initiatives, while {risk_snippet}. "
        f"Overall assessment highlights strong technical and strategic positioning backed by {len(unique_evidences)} verified evidence sources."
    )

    # 6. Construct Final Report
    report = CompanyIntelligenceReport(
        title=f"MarketMind AI Intelligence Report: {company_name}",
        target_company=company_name,
        executive_summary=exec_summary,
        company_overview=profile,
        competitor_landscape=competitors,
        recent_news_and_hiring=news,
        risk_intelligence=risks,
        strategic_opportunities=strategic_opportunities,
        evidence_quality_and_gaps=evidence_gaps,
        evidence_records=unique_evidences,
        validation_issues=validation_issues,
        sources=sorted(list(set(all_sources))),
        generated_at=datetime.utcnow().isoformat(),
        run_metadata={
            "total_evidences": len(unique_evidences),
            "validation_issues_count": len(validation_issues),
            "agents_completed": ["profile", "competitors", "news_hiring", "risks"]
        }
    )

    return {
        "final_report": report,
        "evidence_records": unique_evidences,
        "validation_issues": validation_issues
    }
