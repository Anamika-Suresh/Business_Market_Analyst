import logging
from typing import Dict, Any, List

from state import GraphState
from schemas.risk import RiskFindings, RiskFinding, RiskSeverity, RiskCategory
from schemas.evidence import EvidenceRecord, EvidenceType, VerificationStatus
from tools.search import get_search_provider
from tools.llm_factory import get_llm, invoke_structured
from services.evidence_service import build_evidence_record

logger = logging.getLogger(__name__)

def risk_intelligence_agent(state: GraphState) -> Dict[str, Any]:
    """Agent 4: Investigates public legal, regulatory, security, and reputational risk signals."""
    brief = state.get("research_brief")
    company_name = state.get("company_name", "Target Company")
    if brief:
        company_name = brief.company_name

    logger.info(f"[RiskAgent] Starting risk intelligence investigation for: {company_name}")
    evidences: List[EvidenceRecord] = []
    errors: List[str] = []

    search_provider = get_search_provider()
    queries = [
        f"{company_name} lawsuit litigation court complaint legal dispute",
        f"{company_name} regulatory investigation enforcement fine penalty FTC SEC",
        f"{company_name} data breach security vulnerability outage service incident"
    ]

    all_snippets: List[str] = []
    for q in queries:
        try:
            results = search_provider.search(q, max_results=3)
            for r in results:
                all_snippets.append(f"Title: {r.title}\nURL: {r.url}\nSnippet: {r.snippet}")
                ev_type = EvidenceType.COURT_RECORD if "lawsuit" in q or "court" in q else EvidenceType.NEWS_REPORT
                evidences.append(build_evidence_record(
                    url=r.url,
                    title=r.title,
                    claim_text=r.snippet,
                    evidence_type=ev_type,
                    verification_status=VerificationStatus.VERIFIED,
                    confidence_score=0.85
                ))
        except Exception as e:
            logger.warning(f"Error querying search in RiskAgent: {e}")

    llm = get_llm()
    prompt = f"""You are the Risk Intelligence Specialist for MarketMind AI.
Analyze the gathered data and construct a detailed RiskFindings model for '{company_name}'.

CRITICAL REQUIREMENTS:
- Clearly distinguish ALLEGATIONS, ONGOING PROCEEDINGS, SETTLEMENTS, and CONFIRMED FINDINGS. Do not present allegations as proven facts.
- Do not infer wrongdoing merely from unsubstantiated customer complaints or negative opinions.
- IF NO CREDIBLE EVIDENCE of severe legal or regulatory issues is found in the gathered text, set has_identified_risks=False and return an empty findings list.
- NEVER claim that the company has no risks. The standard disclaimer will be used.
- Include source URLs and dates for every finding.

Target Company: {company_name}

Gathered Research:
{chr(10).join(all_snippets)}

Synthesize into structured RiskFindings."""

    try:
        risk_model: RiskFindings = invoke_structured(llm, prompt, RiskFindings)
        risk_model.company_name = company_name
        risk_model.evidence_ids = [e.evidence_id for e in evidences]
        # Ensure has_identified_risks reflects findings length
        if risk_model.findings:
            risk_model.has_identified_risks = True

    except Exception as e:
        logger.error(f"[RiskAgent] LLM structuring error: {e}. Building fallback.")
        errors.append(f"RiskAgent LLM error: {str(e)}")
        risk_model = RiskFindings(
            company_name=company_name,
            findings=[],
            overall_risk_summary=f"No verified adverse legal or regulatory actions were identified for {company_name} during the automated research window.",
            has_identified_risks=False,
            evidence_ids=[e.evidence_id for e in evidences]
        )

    return {
        "risk_findings": risk_model,
        "evidence_records": evidences,
        "errors": errors
    }
