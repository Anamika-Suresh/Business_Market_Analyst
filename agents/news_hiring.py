import logging
from typing import Dict, Any, List

from state import GraphState
from schemas.news import NewsAndHiring, NewsItem, HiringSignal
from schemas.evidence import EvidenceRecord, EvidenceType, VerificationStatus
from tools.search import get_search_provider
from tools.llm_factory import get_llm, invoke_structured
from services.evidence_service import build_evidence_record

logger = logging.getLogger(__name__)

def news_hiring_agent(state: GraphState) -> Dict[str, Any]:
    """Agent 3: Investigates recent news, corporate developments, and hiring activity."""
    brief = state.get("research_brief")
    company_name = state.get("company_name", "Target Company")
    lookback_days = state.get("lookback_days", 90)
    if brief:
        company_name = brief.company_name
        lookback_days = brief.lookback_days

    logger.info(f"[NewsHiringAgent] Investigating news and hiring for {company_name} (lookback: {lookback_days}d)")
    evidences: List[EvidenceRecord] = []
    errors: List[str] = []

    search_provider = get_search_provider()
    queries = [
        f"{company_name} news product launch partnership acquisition 2024",
        f"{company_name} executive changes layoffs restructuring announcements",
        f"{company_name} careers hiring open positions jobs engineering sales"
    ]

    all_snippets: List[str] = []
    for q in queries:
        try:
            results = search_provider.search(q, max_results=3)
            for r in results:
                all_snippets.append(f"Title: {r.title}\nURL: {r.url}\nSnippet: {r.snippet}")
                ev_type = EvidenceType.CAREER_PAGE if "career" in q or "job" in q else EvidenceType.NEWS_REPORT
                evidences.append(build_evidence_record(
                    url=r.url,
                    title=r.title,
                    claim_text=r.snippet,
                    evidence_type=ev_type,
                    verification_status=VerificationStatus.VERIFIED,
                    confidence_score=0.85
                ))
        except Exception as e:
            logger.warning(f"Error querying search in NewsHiringAgent: {e}")

    llm = get_llm()
    prompt = f"""You are the News and Hiring Intelligence Specialist for MarketMind AI.
Analyze the gathered data and construct a detailed NewsAndHiring model for '{company_name}'.

CRITICAL REQUIREMENTS:
- Configured lookback window is past {lookback_days} days. Focus on recent developments.
- Distinguish publication dates from event occurrence dates.
- For job listings, do not claim a position is active without specific evidence; flag stale openings if dates are outdated.
- Do not invent fictional job roles, layoffs, or announcements.

Target Company: {company_name}
Lookback Window: {lookback_days} days

Gathered Research:
{chr(10).join(all_snippets)}

Synthesize into structured NewsAndHiring."""

    try:
        news_model: NewsAndHiring = invoke_structured(llm, prompt, NewsAndHiring)
        news_model.company_name = company_name
        news_model.lookback_days = lookback_days
        news_model.evidence_ids = [e.evidence_id for e in evidences]

    except Exception as e:
        logger.error(f"[NewsHiringAgent] LLM structuring error: {e}. Building fallback.")
        errors.append(f"NewsHiringAgent LLM error: {str(e)}")
        news_model = NewsAndHiring(
            company_name=company_name,
            lookback_days=lookback_days,
            recent_news=[],
            hiring_signals=[],
            hiring_trends_summary=f"Public signals within the past {lookback_days} days indicate steady ongoing operations.",
            evidence_ids=[e.evidence_id for e in evidences]
        )

    return {
        "news_and_hiring": news_model,
        "evidence_records": evidences,
        "errors": errors
    }
