from tools.search import MockSearchProvider, get_search_provider, SearchResult

def test_mock_search_provider_queries():
    provider = MockSearchProvider()
    
    # Profile query
    profile_results = provider.search("Anthropic founders and leadership", max_results=2)
    assert len(profile_results) == 2
    assert any("Dario Amodei" in r.snippet or "Leadership" in r.title for r in profile_results)
    
    # Competitor query
    comp_results = provider.search("Anthropic competitors vs OpenAI", max_results=2)
    assert len(comp_results) == 2
    assert any("OpenAI" in r.snippet or "Competitors" in r.title for r in comp_results)

    # Risk query
    risk_results = provider.search("Anthropic lawsuit litigation risks", max_results=2)
    assert len(risk_results) > 0
    assert any("Lawsuit" in r.title or "FTC" in r.title for r in risk_results)

def test_mock_search_custom_fixtures():
    custom = {
        "custom_query": [
            SearchResult(title="Custom Title", url="https://custom.com", snippet="Custom snippet text")
        ]
    }
    provider = MockSearchProvider(custom_fixtures=custom)
    res = provider.search("Search for custom_query here")
    assert len(res) == 1
    assert res[0].title == "Custom Title"

def test_get_search_provider_factory():
    mock_prov = get_search_provider("mock")
    assert isinstance(mock_prov, MockSearchProvider)
