import time
import logging
import warnings
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

# Filter out duckduckgo_search renaming deprecation warning
warnings.filterwarnings("ignore", category=RuntimeWarning)

logger = logging.getLogger(__name__)

class SearchResult(BaseModel):
    """Standardized search result across all providers."""
    title: str = Field(description="Page title")
    url: str = Field(description="Direct URL to page")
    snippet: str = Field(description="Text snippet or abstract")
    published_date: Optional[str] = Field(default=None, description="Optional publication date if discovered")

class SearchProvider(ABC):
    """Abstract base provider for web search."""
    @abstractmethod
    def search(self, query: str, max_results: int = 5) -> List[SearchResult]:
        """Perform search query and return standardized results."""
        pass

class DuckDuckGoSearchProvider(SearchProvider):
    """Real web search provider backed by duckduckgo_search."""
    def __init__(self, delay_seconds: float = 0.5):
        self.delay_seconds = delay_seconds

    def search(self, query: str, max_results: int = 5) -> List[SearchResult]:
        try:
            try:
                from ddgs import DDGS
            except ImportError:
                from duckduckgo_search import DDGS
        except ImportError:
            logger.warning("duckduckgo_search/ddgs not installed, returning empty results.")
            return []

        results: List[SearchResult] = []
        try:
            # Respect rate-limits with slight courtesy delay
            time.sleep(self.delay_seconds)
            with DDGS() as ddgs:
                ddg_gen = ddgs.text(query, max_results=max_results)
                for item in ddg_gen:
                    url = item.get("href") or item.get("link") or ""
                    title = item.get("title") or "No title"
                    snippet = item.get("body") or item.get("snippet") or ""
                    if url:
                        results.append(SearchResult(
                            title=title,
                            url=url,
                            snippet=snippet
                        ))
        except Exception as e:
            logger.warning(f"DuckDuckGo search error for query '{query}': {e}")
            # Gracefully return whatever results were collected or empty list
        return results

class MockSearchProvider(SearchProvider):
    """Deterministic mock search provider for testing without network/API dependencies."""
    def __init__(self, custom_fixtures: Optional[Dict[str, List[SearchResult]]] = None):
        self.fixtures = custom_fixtures or {}

    def search(self, query: str, max_results: int = 5) -> List[SearchResult]:
        q_lower = query.lower()

        # Check explicit fixture keys
        for key, results in self.fixtures.items():
            if key.lower() in q_lower:
                return results[:max_results]

        # Built-in contextual responses for mock testing
        if "founder" in q_lower or "leadership" in q_lower or "profile" in q_lower or "overview" in q_lower:
            return [
                SearchResult(
                    title="Anthropic - Company Overview & Leadership Team",
                    url="https://www.anthropic.com/team",
                    snippet="Anthropic was co-founded in 2021 by former OpenAI researchers Dario Amodei (CEO) and Daniela Amodei (President), along with Jack Clark, Sam McCandlish, Tom Brown, and Jared Kaplan. Focuses on safe, steerable AI systems."
                ),
                SearchResult(
                    title="Anthropic Secures Major Strategic Funding",
                    url="https://www.anthropic.com/news/funding",
                    snippet="Anthropic announced over $7 billion in total funding commitments including Series C and strategic investments from Amazon and Google. Headquartered in San Francisco, CA."
                ),
                SearchResult(
                    title="Claude 3 Model Family Announcement",
                    url="https://www.anthropic.com/news/claude-3-family",
                    snippet="Anthropic introduces Claude 3 family of models: Opus, Sonnet, and Haiku, setting new industry benchmarks in reasoning and code generation."
                )
            ][:max_results]

        elif "competitor" in q_lower or "alternative" in q_lower or "vs" in q_lower:
            return [
                SearchResult(
                    title="Top AI Foundation Model Competitors: OpenAI, Google DeepMind, Mistral",
                    url="https://techcrunch.com/2024/02/ai-landscape",
                    snippet="Direct competitors in foundation models include OpenAI (ChatGPT/GPT-4o), Google DeepMind (Gemini), and Mistral AI (Mistral Large). OpenAI targets enterprise and consumer, offering tiered API pricing."
                ),
                SearchResult(
                    title="OpenAI vs Anthropic vs Google - Competitive Positioning",
                    url="https://venturebeat.com/ai/frontier-models-compared",
                    snippet="While OpenAI leads consumer brand awareness, Anthropic focuses heavily on AI safety, Constitutional AI, and enterprise reliability with Claude."
                ),
                SearchResult(
                    title="Open Source LLM Substitutes - Meta Llama",
                    url="https://huggingface.co/blog/open-models",
                    snippet="Meta Llama serves as an open-weights substitute for proprietary APIs, allowing on-premise deployment and zero per-token API licensing costs."
                )
            ][:max_results]

        elif "news" in q_lower or "hiring" in q_lower or "jobs" in q_lower or "partnership" in q_lower:
            return [
                SearchResult(
                    title="Anthropic Expands European Operations with Dublin Hub",
                    url="https://www.reuters.com/technology/anthropic-europe-expansion",
                    snippet="Published 2024-03-12. Anthropic announces expansion into Europe, establishing an engineering and regulatory affairs hub. Hiring senior research scientists and compliance leads."
                ),
                SearchResult(
                    title="Anthropic Career Openings: Systems Engineering & Safety Research",
                    url="https://www.anthropic.com/careers",
                    snippet="Current verified job openings include: Staff Distributed Systems Engineer (San Francisco / Hybrid), Member of Technical Staff - Alignment Science, and Product Manager - Enterprise API."
                ),
                SearchResult(
                    title="Amazon Completes $4 Billion Investment in Anthropic",
                    url="https://www.bloomberg.com/news/articles/2024-03-27/amazon-investment",
                    snippet="Published 2024-03-27. Amazon finalized its $4 billion investment in Anthropic, solidifying AWS as primary cloud provider for mission-critical training workloads."
                )
            ][:max_results]

        elif "risk" in q_lower or "lawsuit" in q_lower or "investigation" in q_lower or "breach" in q_lower:
            return [
                SearchResult(
                    title="Music Publishers File Copyright Lawsuit Against Anthropic",
                    url="https://www.reuters.com/legal/music-publishers-sue-anthropic-lyrics",
                    snippet="Universal Music Group, Concord, and ABKCO filed a copyright infringement lawsuit against Anthropic in Tennessee federal court alleging unauthorized reproduction of song lyrics in training datasets. Anthropic filed a motion to dismiss."
                ),
                SearchResult(
                    title="FTC Launches Inquiry into Big Tech AI Partnerships",
                    url="https://www.ftc.gov/news-events/news/press-releases/2024/01/ftc-inquiry-generative-ai",
                    snippet="The US Federal Trade Commission issued orders to five companies (Alphabet, Amazon, Anthropic, Microsoft, and OpenAI) under Section 6(b) to examine recent investments and cloud partnerships for potential antitrust implications."
                )
            ][:max_results]

        # Generic fallback
        return [
            SearchResult(
                title=f"{query} - Overview and Details",
                url=f"https://example.com/info/{abs(hash(query)) % 1000}",
                snippet=f"Comprehensive informational coverage and public documentation regarding {query}."
            )
        ][:max_results]

def get_search_provider(name: Optional[str] = None) -> SearchProvider:
    """Factory to retrieve configured search provider."""
    from config import config
    provider_name = (name or config.search_provider).lower()
    if provider_name == "duckduckgo":
        return DuckDuckGoSearchProvider()
    return MockSearchProvider()
