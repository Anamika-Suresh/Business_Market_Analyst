from state import GraphState
from agents.competitor_intelligence import competitor_intelligence_agent
from config import config

def test_competitor_intelligence_agent_execution():
    config.llm_provider = "mock"
    config.search_provider = "mock"

    state: GraphState = {
        "company_name": "Anthropic",
        "evidence_records": [],
        "errors": []
    }

    result = competitor_intelligence_agent(state)
    assert "competitor_analysis" in result
    analysis = result["competitor_analysis"]
    assert analysis is not None
    assert analysis.target_company == "Anthropic"
    assert len(analysis.direct_competitors) > 0
    direct_names = [c.name for c in analysis.direct_competitors]
    assert "OpenAI" in direct_names
    assert len(analysis.substitute_products) > 0
    assert len(result["evidence_records"]) > 0
