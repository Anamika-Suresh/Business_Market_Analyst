import logging
from typing import Dict, Any, List

from state import GraphState
from schemas.competitor import CompetitorAnalysis, CompetitorItem
from schemas.evidence import EvidenceRecord, EvidenceType, VerificationStatus
from tools.search import get_search_provider
from tools.llm_factory import get_llm, invoke_structured
from services.evidence_service import build_evidence_record

logger = logging.getLogger(__name__)

def competitor_intelligence_agent(state: GraphState) -> Dict[str, Any]:
    """Agent 2: Identifies competitive landscape, substitutes, pricing, and positioning."""
    brief = state.get("research_brief")
    company_name = state.get("company_name", "Target Company")
    if brief:
        company_name = brief.company_name

    logger.info(f"[CompetitorAgent] Starting competitive intelligence for: {company_name}")
    evidences: List[EvidenceRecord] = []
    errors: List[str] = []

    search_provider = get_search_provider()
    queries = [
        f"{company_name} direct competitors alternatives market landscape",
        f"{company_name} vs competitor pricing comparison features",
        f"{company_name} substitute products open source alternatives"
    ]

    all_snippets: List[str] = []
    for q in queries:
        try:
            results = search_provider.search(q, max_results=3)
            for r in results:
                all_snippets.append(f"Title: {r.title}\nURL: {r.url}\nSnippet: {r.snippet}")
                evidences.append(build_evidence_record(
                    url=r.url,
                    title=r.title,
                    claim_text=r.snippet,
                    evidence_type=EvidenceType.INDUSTRY_ANALYSIS,
                    verification_status=VerificationStatus.VERIFIED,
                    confidence_score=0.8
                ))
        except Exception as e:
            logger.warning(f"Error querying search in CompetitorAgent: {e}")

    llm = get_llm()
    prompt = f"""You are the Competitor Intelligence Specialist for MarketMind AI.
Analyze the gathered data and construct a detailed CompetitorAnalysis model for '{company_name}'.

CRITICAL REQUIREMENTS:
- Clearly separate DIRECT competitors (head-to-head), INDIRECT competitors, and SUBSTITUTE products.
- Do not invent competitors, market share percentages, or fictional pricing.
- Include evidence sources URLs in the competitor records where found.
- If pricing is not publicly disclosed, state 'Quote-based / Tiered' or 'Undisclosed'.

Target Company: {company_name}

Gathered Research:
{chr(10).join(all_snippets)}

Synthesize into structured CompetitorAnalysis."""

    try:
        analysis: CompetitorAnalysis = invoke_structured(llm, prompt, CompetitorAnalysis)
        analysis.target_company = company_name
        analysis.evidence_ids = [e.evidence_id for e in evidences]

    except Exception as e:
        logger.error(f"[CompetitorAgent] LLM structuring error: {e}. Building fallback analysis.")
        errors.append(f"CompetitorAgent LLM error: {str(e)}")
        analysis = CompetitorAnalysis(
            target_company=company_name,
            direct_competitors=[
                CompetitorItem(
                    name="Industry Peers",
                    competitor_type="DIRECT",
                    products_services=["Competitive Enterprise Suite"],
                    target_segment="Enterprise Clients",
                    public_pricing="Quote-based",
                    competitive_positioning="Direct market participant in same vertical",
                    strengths=["Established brand presence"],
                    potential_weaknesses=["Legacy technical debt"],
                    is_verified=False
                )
            ],
            indirect_competitors=[],
            substitute_products=[],
            market_overlap_summary=f"Competitive intelligence synthesis completed with fallback data for {company_name}.",
            evidence_ids=[e.evidence_id for e in evidences]
        )

    return {
        "competitor_analysis": analysis,
        "evidence_records": evidences,
        "errors": errors
    }
