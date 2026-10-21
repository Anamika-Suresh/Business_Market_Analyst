from state import GraphState
from agents.company_profile import company_profile_agent
from config import config

def test_company_profile_agent_execution():
    config.llm_provider = "mock"
    config.search_provider = "mock"

    state: GraphState = {
        "company_name": "Anthropic",
        "company_url": "https://www.anthropic.com",
        "evidence_records": [],
        "errors": []
    }

    result = company_profile_agent(state)
    assert "company_profile" in result
    profile = result["company_profile"]
    assert profile is not None
    assert profile.company_name == "Anthropic"
    assert len(profile.founders) > 0
    assert any("Dario" in f.name for f in profile.founders)
    assert len(result["evidence_records"]) > 0
    assert isinstance(result["errors"], list)
