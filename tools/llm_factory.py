import os
import re
import json
import logging
from typing import Optional, Any, Type, TypeVar, Dict
from pydantic import BaseModel
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import BaseMessage, AIMessage
from langchain_core.outputs import ChatResult, ChatGeneration

from config import config

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)

def extract_json_from_text(text: str) -> Optional[Dict[str, Any]]:
    """Extract and parse JSON object from raw LLM text, markdown codeblocks, or tool envelopes."""
    if not text:
        return None
    text = text.strip()

    # 1. Direct JSON parse
    try:
        parsed = json.loads(text)
        if isinstance(parsed, dict):
            return parsed
    except Exception:
        pass

    # 2. Markdown fenced block ```json ... ```
    match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if match:
        try:
            parsed = json.loads(match.group(1).strip())
            if isinstance(parsed, dict):
                return parsed
        except Exception:
            pass

    # 3. First '{' to last '}'
    first_brace = text.find("{")
    last_brace = text.rfind("}")
    if first_brace != -1 and last_brace > first_brace:
        candidate = text[first_brace:last_brace + 1]
        try:
            parsed = json.loads(candidate)
            if isinstance(parsed, dict):
                return parsed
        except Exception:
            pass

    return None

class MockStructuredRunnable:
    """Mock runnable that returns realistic structured Pydantic models for testing."""
    def __init__(self, schema: Type[T]):
        self.schema = schema

    def invoke(self, input_val: Any, *args, **kwargs) -> Any:
        name = self.schema.__name__
        
        if "CompanyProfile" in name:
            from schemas.company import CompanyProfile, Executive, FundingRound, CompanyMilestone
            return CompanyProfile(
                company_name="Anthropic",
                official_website="https://www.anthropic.com",
                description="AI safety and research company that develops reliable, steerable foundation models including Claude.",
                core_products_or_services=["Claude 3 Opus", "Claude 3 Sonnet", "Claude 3 Haiku", "Anthropic API"],
                industry="Artificial Intelligence / Enterprise Software",
                business_model="B2B API Licensing & B2C Subscription",
                target_customers=["Enterprise Developers", "Financial Institutions", "Healthcare Organizations"],
                founders=[
                    Executive(name="Dario Amodei", title="Co-Founder & CEO", is_founder=True, verified=True),
                    Executive(name="Daniela Amodei", title="Co-Founder & President", is_founder=True, verified=True)
                ],
                key_executives=[
                    Executive(name="Jack Clark", title="Co-Founder & Head of Policy", is_founder=True, verified=True)
                ],
                funding_rounds=[
                    FundingRound(round_name="Series C / Strategic", amount="$4 Billion", announced_date="2024-03-27", lead_investors=["Amazon", "Google"])
                ],
                total_funding="$7.3 Billion",
                headquarters="San Francisco, California, USA",
                operating_regions=["North America", "Europe", "Asia-Pacific"],
                milestones=[
                    CompanyMilestone(date="2021", description="Founded by former OpenAI researchers", significance="Focus on alignment and Constitutional AI"),
                    CompanyMilestone(date="2024", description="Released Claude 3 family of models", significance="Achieved state-of-the-art benchmark scores")
                ],
                evidence_ids=["ev-mock-profile-1", "ev-mock-profile-2"]
            )
        
        elif "CompetitorAnalysis" in name:
            from schemas.competitor import CompetitorAnalysis, CompetitorItem
            return CompetitorAnalysis(
                target_company="Anthropic",
                direct_competitors=[
                    CompetitorItem(
                        name="OpenAI",
                        website="https://openai.com",
                        competitor_type="DIRECT",
                        products_services=["ChatGPT Plus", "GPT-4o", "OpenAI API"],
                        target_segment="Consumer & Enterprise",
                        public_pricing="$20/mo Plus, Usage-based API tiers",
                        competitive_positioning="First-mover market leader with high brand recognition",
                        key_differentiators=["Extensive consumer ecosystem", "Custom GPT store"],
                        strengths=["Dominant developer adoption", "Broad multi-modal ecosystem"],
                        potential_weaknesses=["High operational costs", "Governance and safety scrutiny"],
                        evidence_sources=["https://techcrunch.com/2024/02/ai-landscape"],
                        is_verified=True
                    ),
                    CompetitorItem(
                        name="Google DeepMind",
                        website="https://deepmind.google",
                        competitor_type="DIRECT",
                        products_services=["Gemini 1.5 Pro", "Gemini Ultra", "Vertex AI API"],
                        target_segment="Google Cloud Enterprise & Android Ecosystem",
                        public_pricing="Tiered API pricing on Google Cloud",
                        competitive_positioning="Native multi-modal giant with immense cloud distribution",
                        key_differentiators=["Massive 1M+ context window", "Deep integration into Google Workspace"],
                        strengths=["Vertical integration from TPU chips to products", "Google Cloud distribution"],
                        potential_weaknesses=["Organizational complexity", "Slower enterprise migration cycles"],
                        evidence_sources=["https://venturebeat.com/ai/frontier-models-compared"],
                        is_verified=True
                    )
                ],
                indirect_competitors=[
                    CompetitorItem(
                        name="Mistral AI",
                        website="https://mistral.ai",
                        competitor_type="INDIRECT",
                        products_services=["Mistral Large", "Codestral"],
                        target_segment="European enterprises and developers wanting open weights",
                        public_pricing="Competitive per-token pricing",
                        competitive_positioning="European champion emphasizing open and portable weights",
                        key_differentiators=["European sovereignty compliance", "Lightweight models"],
                        strengths=["High performance per parameter", "Enterprise self-hosting flexibility"],
                        potential_weaknesses=["Smaller capital base than US hyperscalers"],
                        evidence_sources=["https://huggingface.co/blog/open-models"],
                        is_verified=True
                    )
                ],
                substitute_products=[
                    CompetitorItem(
                        name="Meta Llama 3",
                        website="https://ai.meta.com/llama",
                        competitor_type="SUBSTITUTE",
                        products_services=["Llama 3 70B", "Llama 3 405B"],
                        target_segment="Self-hosted infrastructure teams",
                        public_pricing="Open weights (Free commercial license under threshold)",
                        competitive_positioning="Zero API cost alternative with full data ownership",
                        key_differentiators=["Complete model weights control", "On-premise air-gapped deployment"],
                        strengths=["Zero per-call vendor lock-in", "Active open-source community"],
                        potential_weaknesses=["Demands in-house GPU orchestration and infrastructure"],
                        evidence_sources=["https://huggingface.co/blog/open-models"],
                        is_verified=True
                    )
                ],
                market_overlap_summary="Heavy competition with OpenAI and Google in the top-tier enterprise reasoning segment, while open-weights models like Llama apply pricing pressure.",
                evidence_ids=["ev-mock-comp-1"]
            )

        elif "NewsAndHiring" in name:
            from schemas.news import NewsAndHiring, NewsItem, HiringSignal
            return NewsAndHiring(
                company_name="Anthropic",
                lookback_days=90,
                recent_news=[
                    NewsItem(
                        headline="Amazon Finalizes $4 Billion Total Investment in Anthropic",
                        summary="Amazon completed its minority investment in Anthropic, designating AWS as the primary cloud provider.",
                        category="FUNDING",
                        publication_date="2024-03-27",
                        event_date="2024-03-27",
                        source_url="https://www.bloomberg.com/news/articles/2024-03-27/amazon-investment",
                        publisher="Bloomberg",
                        is_dated=True,
                        evidence_id="ev-mock-news-1"
                    ),
                    NewsItem(
                        headline="Anthropic Establishes European Office in Dublin",
                        summary="Anthropic launched a regional engineering and regulatory affairs hub to support EU compliance.",
                        category="ACQUISITION",
                        publication_date="2024-03-12",
                        event_date="2024-03-12",
                        source_url="https://www.reuters.com/technology/anthropic-europe-expansion",
                        publisher="Reuters",
                        is_dated=True,
                        evidence_id="ev-mock-news-2"
                    )
                ],
                hiring_signals=[
                    HiringSignal(
                        role_title="Staff Distributed Systems Engineer",
                        department="Infrastructure",
                        location="San Francisco, CA (Hybrid)",
                        date_posted="2024-03-15",
                        source_url="https://www.anthropic.com/careers",
                        is_active_opening=True,
                        is_stale=False,
                        evidence_id="ev-mock-hiring-1"
                    ),
                    HiringSignal(
                        role_title="Research Scientist - Model Alignment & Safety",
                        department="Alignment Science",
                        location="San Francisco, CA / London, UK",
                        date_posted="2024-03-10",
                        source_url="https://www.anthropic.com/careers",
                        is_active_opening=True,
                        is_stale=False,
                        evidence_id="ev-mock-hiring-2"
                    )
                ],
                hiring_trends_summary="Intense hiring in large-scale distributed training infrastructure, alignment science, and European enterprise solutions.",
                evidence_ids=["ev-mock-news-1", "ev-mock-news-2", "ev-mock-hiring-1"]
            )

        elif "RiskFindings" in name:
            from schemas.risk import RiskFindings, RiskFinding, RiskSeverity, RiskCategory
            return RiskFindings(
                company_name="Anthropic",
                findings=[
                    RiskFinding(
                        finding_id="risk-1",
                        title="Universal Music Group Copyright Litigation",
                        category=RiskCategory.LITIGATION,
                        nature="ONGOING_PROCEEDING",
                        summary="Major music publishers filed suit in US Federal Court alleging training datasets included copyrighted song lyrics without authorization.",
                        severity=RiskSeverity.HIGH,
                        incident_date="2023-10-18",
                        source_url="https://www.reuters.com/legal/music-publishers-sue-anthropic-lyrics",
                        publisher="Reuters",
                        verified=True,
                        caveats="Anthropic has filed motions to dismiss and argues fair use in AI training datasets.",
                        evidence_id="ev-mock-risk-1"
                    ),
                    RiskFinding(
                        finding_id="risk-2",
                        title="FTC Section 6(b) Inquiry into Cloud AI Partnerships",
                        category=RiskCategory.REGULATORY,
                        nature="ONGOING_PROCEEDING",
                        summary="US FTC issued orders to review multi-billion cloud and compute agreements with Amazon and Google for market competition implications.",
                        severity=RiskSeverity.MEDIUM,
                        incident_date="2024-01-25",
                        source_url="https://www.ftc.gov/news-events/news/press-releases/2024/01/ftc-inquiry-generative-ai",
                        publisher="FTC Official Release",
                        verified=True,
                        caveats="Standard investigative inquiry into industry partnerships; no formal violation or enforcement penalty has been alleged.",
                        evidence_id="ev-mock-risk-2"
                    )
                ],
                overall_risk_summary="Risks concentrate around training data copyright litigation and antitrust regulatory scrutiny over hyperscaler cloud partnerships.",
                has_identified_risks=True,
                evidence_ids=["ev-mock-risk-1", "ev-mock-risk-2"]
            )

        try:
            return self.schema()
        except Exception:
            return None

class MockChatModel(BaseChatModel):
    """Custom mock chat model for robust offline tests and verification."""
    def _generate(self, messages: list[BaseMessage], stop: Optional[list[str]] = None, **kwargs) -> ChatResult:
        content = "Mock LLM synthesis output generated for testing."
        return ChatResult(generations=[ChatGeneration(message=AIMessage(content=content))])

    @property
    def _llm_type(self) -> str:
        return "mock_chat_model"

    def with_structured_output(self, schema: Type[T], **kwargs) -> Any:
        return MockStructuredRunnable(schema)

def get_llm(
    provider: Optional[str] = None,
    model: Optional[str] = None,
    temperature: float = 0.2
) -> Any:
    """Retrieve configured LLM instance with fallback to MockChatModel."""
    selected_provider = (provider or config.llm_provider).lower()
    selected_model = model or config.get_resolved_model()

    if selected_provider == "groq":
        api_key = config.groq_api_key or os.getenv("GROQ_API_KEY")
        if not api_key:
            logger.warning("GROQ_API_KEY not configured. Falling back to MockChatModel for testing.")
            return MockChatModel()
        try:
            from langchain_groq import ChatGroq
            return ChatGroq(
                model=selected_model,
                groq_api_key=api_key,
                temperature=temperature,
                request_timeout=35.0,
                max_retries=2
            )
        except Exception as e:
            logger.warning(f"Error initializing ChatGroq: {e}. Falling back to MockChatModel.")
            return MockChatModel()

    elif selected_provider == "gemini":
        api_key = config.google_api_key or os.getenv("GOOGLE_API_KEY")
        if not api_key:
            logger.warning("GOOGLE_API_KEY not configured. Falling back to MockChatModel for testing.")
            return MockChatModel()
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
            return ChatGoogleGenerativeAI(
                model=selected_model,
                google_api_key=api_key,
                temperature=temperature,
                timeout=30.0,
                max_retries=2
            )
        except Exception as e:
            logger.warning(f"Error initializing ChatGoogleGenerativeAI: {e}. Falling back to MockChatModel.")
            return MockChatModel()

    return MockChatModel()

def invoke_structured(llm: Any, prompt: str, schema: Type[T]) -> T:
    """Resilient structured output invocation.
    
    1. Runs with_structured_output(schema).
    2. If Groq/provider tool choice error occurs, extracts JSON from 'failed_generation' in exception.
    3. If needed, falls back to direct clean JSON prompt without tool wrappers.
    """
    if isinstance(llm, MockChatModel):
        return llm.with_structured_output(schema).invoke(prompt)

    import time
    for attempt in range(3):
        # Attempt 1: Standard structured output
        try:
            structured_runner = llm.with_structured_output(schema)
            return structured_runner.invoke(prompt)
        except Exception as e:
            err_str = str(e)
            if "429" in err_str or "rate_limit" in err_str.lower() or "too many requests" in err_str.lower():
                wait_time = 3.0 * (attempt + 1)
                logger.info(f"[StructuredInvoke] Groq rate limit (429) hit. Backing off for {wait_time:.1f}s (attempt {attempt + 1}/3)...")
                time.sleep(wait_time)
                continue

            logger.debug(f"[StructuredInvoke] Initial tool-call attempt yielded: {e}. Attempting recovery.")
            
            # Check for failed_generation inside error payload
            failed_gen = None
            if hasattr(e, "body") and isinstance(e.body, dict):
                failed_gen = e.body.get("error", {}).get("failed_generation")
            elif hasattr(e, "response") and hasattr(e.response, "json"):
                try:
                    failed_gen = e.response.json().get("error", {}).get("failed_generation")
                except Exception:
                    pass
            if not failed_gen:
                m = re.search(r"failed_generation['\":\s]+(.*?)(?:'\}|\"\}|$)", err_str, re.DOTALL)
                if m:
                    failed_gen = m.group(1)

            if failed_gen:
                data = extract_json_from_text(failed_gen)
                if data:
                    if "arguments" in data and isinstance(data["arguments"], dict):
                        data = data["arguments"]
                    try:
                        return schema.model_validate(data)
                    except Exception as ve:
                        logger.debug(f"[StructuredInvoke] Failed to validate failed_generation: {ve}")

        # Attempt 2: Direct prompt request for pure JSON (bypassing tool-calling strictness)
        clean_prompt = (
            f"{prompt}\n\n"
            f"CRITICAL: Output ONLY a single, valid JSON object matching the {schema.__name__} schema.\n"
            f"Do not include markdown code block syntax (like ```json), no explanations, and no preamble."
        )
        try:
            res = llm.invoke(clean_prompt)
            text = res.content if hasattr(res, "content") else str(res)
            data = extract_json_from_text(text)
            if data:
                if "arguments" in data and isinstance(data["arguments"], dict):
                    data = data["arguments"]
                return schema.model_validate(data)
        except Exception as e:
            err_str = str(e)
            if "429" in err_str or "rate_limit" in err_str.lower() or "too many requests" in err_str.lower():
                wait_time = 3.0 * (attempt + 1)
                logger.info(f"[StructuredInvoke] Groq rate limit (429) on fallback. Backing off for {wait_time:.1f}s...")
                time.sleep(wait_time)
                continue
            logger.debug(f"[StructuredInvoke] Direct JSON prompt attempt error: {e}")

    raise RuntimeError(f"Could not synthesize valid {schema.__name__} from LLM response after retries.")
