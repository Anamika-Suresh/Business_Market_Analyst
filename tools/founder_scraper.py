import re
import json
import logging
from typing import List, Optional, Dict, Any
from bs4 import BeautifulSoup
from schemas.company import Executive

logger = logging.getLogger(__name__)

FOUNDER_TITLES = [
    "founder", "co-founder", "cofounder", "co founder",
    "chief executive officer", "ceo", "president", "chief technology officer", "cto",
    "chief operating officer", "coo", "chief scientist"
]

def _is_founder_or_exec_title(title: str) -> bool:
    t = title.lower()
    return any(ft in t for ft in FOUNDER_TITLES)

def _is_founder_title(title: str) -> bool:
    t = title.lower()
    return "founder" in t

def extract_founders_from_html(html: str, source_url: str = "") -> List[Executive]:
    """Parse HTML and extract verified founder & leadership executives.
    
    Inspects:
    1. Schema.org JSON-LD scripts (Person, Organization.founder, Organization.alumni).
    2. Semantic HTML elements & team/leadership card structures.
    3. Microdata and anchor links for social/LinkedIn profiles.
    """
    executives: List[Executive] = []
    seen_names = set()

    if not html or not html.strip():
        return executives

    soup = BeautifulSoup(html, "html.parser")

    # 1. Parse Schema.org JSON-LD scripts
    for script in soup.find_all("script", type="application/ld+json"):
        try:
            raw_text = script.string
            if not raw_text:
                continue
            data = json.loads(raw_text.strip())
            items = data if isinstance(data, list) else [data]

            for item in items:
                if not isinstance(item, dict):
                    continue
                
                # Check for Organization with founders
                if item.get("@type") in ("Organization", "Corporation"):
                    for key in ("founder", "founders"):
                        founders_data = item.get(key, [])
                        if isinstance(founders_data, dict):
                            founders_data = [founders_data]
                        for f in founders_data:
                            if isinstance(f, dict):
                                name = f.get("name")
                                job_title = f.get("jobTitle") or "Co-Founder"
                                same_as = f.get("sameAs")
                                linkedin = same_as if isinstance(same_as, str) and "linkedin.com" in same_as else None
                                if name and name.lower() not in seen_names:
                                    seen_names.add(name.lower())
                                    executives.append(Executive(
                                        name=name.strip(),
                                        title=job_title.strip(),
                                        bio=f.get("description"),
                                        linkedin_url=linkedin,
                                        is_founder=_is_founder_title(job_title),
                                        verified=True
                                    ))

                # Direct Person records
                elif item.get("@type") == "Person":
                    name = item.get("name")
                    job_title = item.get("jobTitle") or ""
                    if name and _is_founder_or_exec_title(job_title) and name.lower() not in seen_names:
                        seen_names.add(name.lower())
                        same_as = item.get("sameAs")
                        linkedin = same_as if isinstance(same_as, str) and "linkedin.com" in same_as else None
                        executives.append(Executive(
                            name=name.strip(),
                            title=job_title.strip() if job_title else "Executive",
                            bio=item.get("description"),
                            linkedin_url=linkedin,
                            is_founder=_is_founder_title(job_title),
                            verified=True
                        ))
        except Exception as e:
            logger.debug(f"JSON-LD parsing error: {e}")

    # 2. Semantic Team/Leadership Cards Parsing
    team_selectors = [
        ".team-member", ".leader-card", ".leadership-card", ".executive-card",
        ".profile-card", ".person", ".team-card", "[data-team-member]",
        ".founder-item", ".bio-card", ".member-card"
    ]
    cards = soup.select(", ".join(team_selectors))

    # If no specialized classes found, search containers with 'team', 'leaders', 'about'
    if not cards:
        for section in soup.find_all(["section", "div"], class_=re.compile(r"team|leader|exec|founder", re.I)):
            candidate_cards = section.find_all(["div", "article", "li"], class_=re.compile(r"card|item|member|col", re.I))
            if candidate_cards:
                cards.extend(candidate_cards)

    for card in cards:
        name_elem = card.find(["h2", "h3", "h4", "h5", "strong", ".name"])
        title_elem = card.find(["p", "span", "div", ".title", ".role"], class_=re.compile(r"title|role|position|job", re.I))

        if not name_elem:
            continue

        name = name_elem.get_text(strip=True)
        # Avoid long sentences or button text
        if not name or len(name.split()) > 4 or len(name) > 50:
            continue

        title = title_elem.get_text(strip=True) if title_elem else ""
        if not title:
            # Check adjacent sibling
            next_p = name_elem.find_next_sibling(["p", "span"])
            if next_p:
                title = next_p.get_text(strip=True)

        if not _is_founder_or_exec_title(title):
            continue

        if name.lower() in seen_names:
            continue

        seen_names.add(name.lower())

        # Extract LinkedIn if available
        linkedin_link = card.find("a", href=re.compile(r"linkedin\.com/in/", re.I))
        linkedin_url = linkedin_link["href"] if linkedin_link and linkedin_link.get("href") else None

        # Extract short bio if available
        bio_elem = card.find(["p", "div"], class_=re.compile(r"bio|desc|text", re.I))
        bio = bio_elem.get_text(strip=True) if bio_elem else None

        executives.append(Executive(
            name=name,
            title=title,
            bio=bio,
            linkedin_url=linkedin_url,
            is_founder=_is_founder_title(title),
            verified=True
        ))

    return executives

async def extract_founders_with_playwright(url: str, timeout_ms: int = 15000) -> List[Executive]:
    """Execute dynamic Playwright session for SPAs and Javascript-rendered leadership pages."""
    try:
        from playwright.async_api import async_playwright
    except ImportError:
        logger.info("Playwright not installed or available. Falling back to HTTP extraction.")
        return []

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            # Set polite headers and viewport
            await page.set_extra_http_headers({
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 MarketMind/1.0"
            })
            await page.goto(url, timeout=timeout_ms, wait_until="domcontentloaded")
            # Wait briefly for potential client-side render
            await page.wait_for_timeout(1000)
            content = await page.content()
            await browser.close()
            return extract_founders_from_html(content, source_url=url)
    except Exception as e:
        logger.warning(f"Playwright execution failed for {url}: {e}. Fallback will be used.")
        return []

def extract_founders(url: str, html: Optional[str] = None) -> List[Executive]:
    """Unified entrypoint: parses provided HTML or fetches page to extract founders/executives."""
    if html:
        return extract_founders_from_html(html, source_url=url)
    
    # Try fetching with requests first
    from tools.web_extractor import WebExtractor
    extractor = WebExtractor()
    extracted = extractor.extract(url)
    if extracted.success and extracted.text:
        # Note: WebExtractor.extract caches results, but parse_html stripped scripts
        # We can request raw page via session for schema.org parsing
        try:
            resp = extractor.session.get(url, timeout=10)
            if resp.status_code == 200:
                results = extract_founders_from_html(resp.text, source_url=url)
                if results:
                    return results
        except Exception:
            pass

    return []
