from state import GraphState
from agents.news_hiring import news_hiring_agent
from config import config

def test_news_hiring_agent_execution():
    config.llm_provider = "mock"
    config.search_provider = "mock"

    state: GraphState = {
        "company_name": "Anthropic",
        "lookback_days": 90,
        "evidence_records": [],
        "errors": []
    }

    result = news_hiring_agent(state)
    assert "news_and_hiring" in result
    news = result["news_and_hiring"]
    assert news is not None
    assert news.company_name == "Anthropic"
    assert news.lookback_days == 90
    assert len(news.recent_news) > 0
    assert news.recent_news[0].source_url.startswith("http")
    assert len(news.hiring_signals) > 0
    assert len(result["evidence_records"]) > 0
