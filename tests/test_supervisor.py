from nodes.supervisor import supervisor_node
from state import GraphState

def test_supervisor_valid_company():
    state: GraphState = {
        "company_name": "Anthropic",
        "company_url": "https://www.anthropic.com",
        "lookback_days": 60,
        "user_priorities": "Safety research"
    }
    result = supervisor_node(state)
    brief = result["research_brief"]
    assert brief is not None
    assert brief.company_name == "Anthropic"
    assert brief.company_url == "https://www.anthropic.com"
    assert brief.lookback_days == 60
    assert brief.is_ambiguous is False
    assert "anthropic.com" in brief.identified_domains
    assert len(result["errors"]) == 0

def test_supervisor_infer_name_from_url():
    state: GraphState = {
        "company_name": "",
        "company_url": "https://www.stripe.com"
    }
    result = supervisor_node(state)
    brief = result["research_brief"]
    assert brief is not None
    assert brief.company_name == "Stripe"
    assert result["company_name"] == "Stripe"

def test_supervisor_ambiguous_name_detection():
    state: GraphState = {
        "company_name": "Apple",
        "company_url": None
    }
    result = supervisor_node(state)
    brief = result["research_brief"]
    assert brief is not None
    assert brief.is_ambiguous is True
    assert brief.clarification_message is not None
    assert "official website URL" in brief.clarification_message

def test_supervisor_empty_input_validation():
    state: GraphState = {
        "company_name": "",
        "company_url": None
    }
    result = supervisor_node(state)
    assert len(result["errors"]) > 0
    assert "Validation failed" in result["errors"][0]
