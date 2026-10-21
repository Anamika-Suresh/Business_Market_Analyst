import re
import time
import logging
from typing import Dict, Optional
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

class WebExtractionResult:
    def __init__(
        self,
        url: str,
        title: str,
        text: str,
        success: bool = True,
        status_code: int = 200,
        published_date: Optional[str] = None,
        publisher: str = "Unknown",
        error: Optional[str] = None
    ):
        self.url = url
        self.title = title
        self.text = text
        self.success = success
        self.status_code = status_code
        self.published_date = published_date
        self.publisher = publisher
        self.error = error

    def to_dict(self) -> Dict:
        return {
            "url": self.url,
            "title": self.title,
            "text": self.text,
            "success": self.success,
            "status_code": self.status_code,
            "published_date": self.published_date,
            "publisher": self.publisher,
            "error": self.error,
        }

class WebExtractor:
    """Robust web content extraction with caching, sanitization, and rate-limiting."""

    def __init__(self, timeout: int = 12, max_length: int = 8000, cache_enabled: bool = True):
        self.timeout = timeout
        self.max_length = max_length
        self.cache_enabled = cache_enabled
        self._cache: Dict[str, WebExtractionResult] = {}
        self._last_request_per_domain: Dict[str, float] = {}
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 MarketMind/1.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
        })

    def _get_domain(self, url: str) -> str:
        try:
            return urlparse(url).netloc.lower()
        except Exception:
            return ""

    def _respect_domain_politeness(self, domain: str, delay_seconds: float = 0.5):
        """Enforce domain-level politeness interval."""
        if not domain:
            return
        last_time = self._last_request_per_domain.get(domain, 0)
        elapsed = time.time() - last_time
        if elapsed < delay_seconds:
            time.sleep(delay_seconds - elapsed)
        self._last_request_per_domain[domain] = time.time()

    def extract(self, url: str) -> WebExtractionResult:
        """Extract clean readable text and metadata from URL."""
        if not url or not url.startswith("http"):
            return WebExtractionResult(
                url=url,
                title="",
                text="",
                success=False,
                error="Invalid or non-HTTP URL provided"
            )

        if self.cache_enabled and url in self._cache:
            return self._cache[url]

        domain = self._get_domain(url)
        self._respect_domain_politeness(domain)

        try:
            resp = self.session.get(url, timeout=self.timeout, allow_redirects=True)
            if resp.status_code >= 400:
                result = WebExtractionResult(
                    url=url,
                    title="",
                    text="",
                    success=False,
                    status_code=resp.status_code,
                    publisher=domain,
                    error=f"HTTP status {resp.status_code}"
                )
                if self.cache_enabled:
                    self._cache[url] = result
                return result

            html = resp.text
            result = self.parse_html(html, url=url, publisher=domain)
            if self.cache_enabled:
                self._cache[url] = result
            return result

        except requests.Timeout:
            return WebExtractionResult(
                url=url,
                title="",
                text="",
                success=False,
                publisher=domain,
                error="Connection timed out"
            )
        except Exception as e:
            return WebExtractionResult(
                url=url,
                title="",
                text="",
                success=False,
                publisher=domain,
                error=f"Extraction failed: {str(e)}"
            )

    def parse_html(self, html_content: str, url: str = "", publisher: str = "") -> WebExtractionResult:
        """Parse raw HTML string into clean text and metadata."""
        try:
            soup = BeautifulSoup(html_content, "html.parser")

            # Extract Title
            title = ""
            if soup.title and soup.title.string:
                title = soup.title.string.strip()
            elif soup.find("h1"):
                title = soup.find("h1").get_text(strip=True)

            # Extract published date from meta tags
            date_published = None
            date_meta = soup.find("meta", attrs={"property": "article:published_time"}) or \
                        soup.find("meta", attrs={"name": "date"}) or \
                        soup.find("meta", attrs={"name": "publish-date"}) or \
                        soup.find("time")

            if date_meta:
                if date_meta.name == "time" and date_meta.get("datetime"):
                    date_published = date_meta["datetime"]
                elif date_meta.get("content"):
                    date_published = date_meta["content"]

            # Remove scripts, styles, forms, headers, navigation, footers
            for elem in soup(["script", "style", "noscript", "svg", "nav", "footer", "header", "form"]):
                elem.decompose()

            # Clean and normalize text
            text = soup.get_text(separator="\n", strip=True)
            # Remove excessive consecutive newlines
            text = re.sub(r"\n\s*\n+", "\n\n", text)

            # Limit text length to prevent huge context bloat
            if len(text) > self.max_length:
                text = text[:self.max_length] + "\n...[truncated]"

            if not publisher and url:
                publisher = self._get_domain(url)

            return WebExtractionResult(
                url=url,
                title=title or "Untitled Page",
                text=text,
                success=True,
                status_code=200,
                published_date=date_published,
                publisher=publisher or "Web"
            )
        except Exception as e:
            return WebExtractionResult(
                url=url,
                title="",
                text="",
                success=False,
                error=f"HTML parsing error: {str(e)}"
            )
