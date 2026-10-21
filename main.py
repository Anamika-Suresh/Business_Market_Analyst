import sys
import os
import argparse
import logging
from pathlib import Path
from typing import Optional

# Ensure UTF-8 output on Windows terminal
if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from config import config
from graph import get_compiled_graph

# Setup clean console logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("MarketMind")

def parse_args():
    parser = argparse.ArgumentParser(
        description="MarketMind AI — Multi-Agent Company Intelligence Platform",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --company "Anthropic" --url "https://www.anthropic.com"
  python main.py --company "Stripe" --days 60 --provider groq
  python main.py --company "Anthropic" --mock-search --mock-llm
        """
    )
    parser.add_argument(
        "--company", "-c",
        type=str,
        help="Target company name (e.g. 'Anthropic', 'OpenAI', 'Databricks')"
    )
    parser.add_argument(
        "--url", "-u",
        type=str,
        help="Target company website URL (e.g. 'https://www.anthropic.com')"
    )
    parser.add_argument(
        "--days", "-d",
        type=int,
        default=90,
        help="Lookback period in days for news and hiring signals (default: 90)"
    )
    parser.add_argument(
        "--focus", "-f",
        type=str,
        default=None,
        help="Specific research priorities or focus areas (e.g. 'Enterprise revenue, API pricing')"
    )
    parser.add_argument(
        "--output-dir", "-o",
        type=str,
        default="runs",
        help="Directory where generated reports and metadata are saved (default: runs)"
    )
    parser.add_argument(
        "--provider",
        choices=["groq", "gemini", "mock"],
        default=None,
        help="LLM provider override (default from config/env: groq)"
    )
    parser.add_argument(
        "--model",
        type=str,
        default=None,
        help="LLM model name override (e.g. 'llama-3.3-70b-versatile', 'gemini-1.5-flash')"
    )
    parser.add_argument(
        "--mock-search",
        action="store_true",
        help="Use deterministic mock search provider (offline testing without web queries)"
    )
    parser.add_argument(
        "--mock-llm",
        action="store_true",
        help="Use deterministic mock LLM provider (offline testing without API keys)"
    )
    return parser.parse_args()

def run_marketmind(
    company: Optional[str] = None,
    url: Optional[str] = None,
    days: int = 90,
    focus: Optional[str] = None,
    output_dir: str = "runs",
    provider: Optional[str] = None,
    model: Optional[str] = None,
    mock_search: bool = False,
    mock_llm: bool = False
):
    """Programmatic API to invoke the multi-agent MarketMind AI workflow."""
    if not company and not url:
        print("\n❌ Error: Please specify either --company or --url to start research.")
        print("Run `python main.py --help` for usage details.\n")
        return None

    # Apply runtime configuration overrides
    if provider:
        config.llm_provider = provider  # type: ignore
    if model:
        config.llm_model = model
    if mock_llm:
        config.llm_provider = "mock"
    if mock_search:
        config.search_provider = "mock"
    if output_dir:
        config.output_dir = output_dir

    print("=" * 68)
    print(" 🚀 MarketMind AI — Multi-Agent Company Intelligence Platform")
    print("=" * 68)
    print(f" • Target Company   : {company or 'Inferred from URL'}")
    print(f" • Target URL       : {url or 'Auto-discovered'}")
    print(f" • Lookback Window  : {days} days")
    print(f" • LLM Provider     : {config.llm_provider} ({config.get_resolved_model()})")
    print(f" • Search Provider  : {config.search_provider}")
    print(f" • Output Directory : {config.output_dir}")
    print("-" * 68)

    # Compile workflow
    graph = get_compiled_graph()

    # Initial state
    initial_state = {
        "company_name": company or "",
        "company_url": url,
        "lookback_days": days,
        "user_priorities": focus,
        "evidence_records": [],
        "validation_issues": [],
        "errors": [],
        "run_metadata": {}
    }

    print("\n⏳ [1/4] Supervisor resolving company identity and research brief...")
    print("⏳ [2/4] Executing 4 Specialist Agents in PARALLEL via LangGraph...")
    print("      ├── Company Profile Agent")
    print("      ├── Competitor Intelligence Agent")
    print("      ├── News & Hiring Agent")
    print("      └── Risk Intelligence Agent")

    result = graph.invoke(initial_state)

    print("⏳ [3/4] Synthesizing findings and auditing cross-domain evidence...")
    print("⏳ [4/4] Persisting Markdown, JSON, and Run Metadata reports...\n")

    report = result.get("final_report")
    run_meta = result.get("run_metadata") or {}
    report_md = run_meta.get("report_md")
    report_json = run_meta.get("report_json")

    if report and report_md:
        print("=" * 68)
        print(" 🎉 Intelligence Investigation Completed Successfully!")
        print("=" * 68)
        print(f" • Executive Summary:\n   {report.executive_summary[:280]}...\n")
        print(f" • Total Evidence Records Audited : {len(report.evidence_records)}")
        print(f" • Flagged Validation Issues      : {len(report.validation_issues)}")
        print(f" • Markdown Report Saved          : {report_md}")
        print(f" • JSON Report Saved              : {report_json}")
        print("=" * 68)
        return result
    else:
        errors = result.get("errors", [])
        print("⚠️ Investigation concluded with errors:")
        for err in errors:
            print(f" - {err}")
        return result

def main():
    args = parse_args()
    run_marketmind(
        company=args.company,
        url=args.url,
        days=args.days,
        focus=args.focus,
        output_dir=args.output_dir,
        provider=args.provider,
        model=args.model,
        mock_search=args.mock_search,
        mock_llm=args.mock_llm
    )

if __name__ == "__main__":
    main()
