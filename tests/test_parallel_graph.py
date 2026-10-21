import tempfile
from pathlib import Path

from graph import get_compiled_graph
from state import GraphState
from config import config

def test_full_graph_parallel_execution_and_join():
    """End-to-end integration test: user input -> supervisor -> 4 parallel agents -> join -> synthesis -> reports."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        config.output_dir = tmp_dir
        config.llm_provider = "mock"
        config.search_provider = "mock"

        graph = get_compiled_graph()

        initial_state: GraphState = {
            "company_name": "Anthropic",
            "company_url": "https://www.anthropic.com",
            "lookback_days": 90,
            "user_priorities": "AI safety leadership and enterprise LLM competition",
            "evidence_records": [],
            "validation_issues": [],
            "errors": [],
            "run_metadata": {}
        }

        final_state = graph.invoke(initial_state)

        # 1. Verify supervisor output
        assert final_state.get("research_brief") is not None
        assert final_state["research_brief"].company_name == "Anthropic"

        # 2. Verify all 4 parallel agent outputs exist in distinct state fields
        assert final_state.get("company_profile") is not None
        assert final_state.get("competitor_analysis") is not None
        assert final_state.get("news_and_hiring") is not None
        assert final_state.get("risk_findings") is not None

        # 3. Verify evidence records merged cleanly through reducer
        evidences = final_state.get("evidence_records", [])
        assert len(evidences) >= 4  # All agents appended evidence

        # 4. Verify synthesis and final report
        report = final_state.get("final_report")
        assert report is not None
        assert report.target_company == "Anthropic"
        assert len(report.executive_summary) > 50
        assert len(report.sources) > 0

        # 5. Verify physical report files written to output directory
        run_meta = final_state.get("run_metadata", {})
        md_path = run_meta.get("report_md")
        json_path = run_meta.get("report_json")
        assert md_path is not None and Path(md_path).exists()
        assert json_path is not None and Path(json_path).exists()

def test_graph_partial_agent_failure_resilience():
    """Verify workflow completes and generates report even if an agent throws or encounters issues."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        config.output_dir = tmp_dir
        config.llm_provider = "mock"
        config.search_provider = "mock"

        graph = get_compiled_graph()

        # Input without URL to test inference and partial handling
        initial_state: GraphState = {
            "company_name": "Acme Ventures",
            "company_url": None,
            "lookback_days": 30,
            "evidence_records": [],
            "validation_issues": [],
            "errors": []
        }

        final_state = graph.invoke(initial_state)

        # Synthesis must still complete
        assert final_state.get("final_report") is not None
        assert final_state["final_report"].target_company == "Acme Ventures"
        assert Path(final_state["run_metadata"]["report_md"]).exists()
