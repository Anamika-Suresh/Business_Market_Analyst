import logging
from datetime import datetime
from urllib.parse import urlparse
from typing import Dict, Any

from state import GraphState
from schemas.report import ResearchBrief

logger = logging.getLogger(__name__)

AMBIGUOUS_NAMES = {"apple", "target", "meta", "box", "square", "block", "oracle", "stripe", "uber", "ford"}

def supervisor_node(state: GraphState) -> Dict[str, Any]:
    """Supervisor Node: validates user input, resolves company identity, and builds shared ResearchBrief."""
    company_name = state.get("company_name", "").strip()
    company_url = state.get("company_url")
    lookback_days = state.get("lookback_days", 90)
    user_priorities = state.get("user_priorities")

    # If company_name is missing but URL is provided, infer name from URL
    if not company_name and company_url:
        parsed = urlparse(company_url)
        netloc = parsed.netloc or parsed.path
        parts = netloc.replace("www.", "").split(".")
        if parts:
            company_name = parts[0].capitalize()

    # Basic input validation
    if not company_name:
        error_msg = "Validation failed: Neither company name nor valid website URL was provided."
        logger.error(error_msg)
        return {
            "errors": [error_msg],
            "research_brief": ResearchBrief(
                company_name="Unknown",
                is_ambiguous=True,
                clarification_message=error_msg
            )
        }

    # Normalize URL if present
    normalized_url = company_url
    if normalized_url and not normalized_url.startswith(("http://", "https://")):
        normalized_url = f"https://{normalized_url}"

    # Ambiguity check
    is_ambiguous = False
    clarification_msg = None
    if company_name.lower() in AMBIGUOUS_NAMES and not normalized_url:
        is_ambiguous = True
        clarification_msg = (
            f"The company name '{company_name}' may refer to multiple prominent entities or common words. "
            f"Providing an official website URL (e.g. https://www.{company_name.lower()}.com) helps avoid confusion."
        )

    # Derive domains
    identified_domains = []
    if normalized_url:
        parsed = urlparse(normalized_url)
        if parsed.netloc:
            netloc = parsed.netloc.lower()
            clean_domain = netloc.replace("www.", "")
            identified_domains.append(netloc)
            if clean_domain not in identified_domains:
                identified_domains.append(clean_domain)

    brief = ResearchBrief(
        company_name=company_name,
        company_url=normalized_url,
        lookback_days=lookback_days,
        research_date=datetime.utcnow().strftime("%Y-%m-%d"),
        focus_areas=["profile", "competitors", "news_hiring", "risks"],
        identified_domains=identified_domains,
        user_priorities=user_priorities,
        is_ambiguous=is_ambiguous,
        clarification_message=clarification_msg
    )

    return {
        "company_name": company_name,
        "company_url": normalized_url,
        "research_brief": brief,
        "errors": []
    }
