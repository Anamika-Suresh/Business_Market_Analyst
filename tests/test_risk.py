from state import GraphState
from agents.risk_intelligence import risk_intelligence_agent
from config import config

def test_risk_intelligence_agent_execution():
    config.llm_provider = "mock"
    config.search_provider = "mock"

    state: GraphState = {
        "company_name": "Anthropic",
        "evidence_records": [],
        "errors": []
    }

    result = risk_intelligence_agent(state)
    assert "risk_findings" in result
    risks = result["risk_findings"]
    assert risks is not None
    assert risks.company_name == "Anthropic"
    assert len(risks.findings) > 0
    # Must distinguish allegations vs findings
    natures = [rf.nature for rf in risks.findings]
    assert any(n in ("ONGOING_PROCEEDING", "ALLEGATION", "SETTLEMENT") for n in natures)
    assert len(result["evidence_records"]) > 0
    # Must have standard disclaimer
    assert "No relevant public evidence" in risks.no_risk_disclaimer
