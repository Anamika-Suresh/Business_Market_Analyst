import logging
from typing import Dict, Any

from state import GraphState
from services.report_service import save_report
from config import config

logger = logging.getLogger(__name__)

def report_generator_node(state: GraphState) -> Dict[str, Any]:
    """Report Generator Node: Persists Markdown, JSON, and metadata files into runs/."""
    report = state.get("final_report")
    if not report:
        error_msg = "Cannot generate reports: final_report missing from state."
        logger.error(error_msg)
        return {"errors": [error_msg]}

    output_dir = config.output_dir
    run_meta = state.get("run_metadata") or {}
    run_meta.update({
        "model": config.get_resolved_model(),
        "llm_provider": config.llm_provider,
        "search_provider": config.search_provider,
        "errors": state.get("errors", [])
    })

    try:
        md_path, json_path, meta_path = save_report(
            report=report,
            output_dir=output_dir,
            run_metadata=run_meta
        )
        logger.info(f"Successfully generated reports in: {md_path.parent}")
        run_meta.update({
            "report_md": str(md_path),
            "report_json": str(json_path),
            "run_meta": str(meta_path)
        })
    except Exception as e:
        logger.error(f"Error persisting reports: {e}")
        return {"errors": [f"Report generation error: {str(e)}"]}

    return {
        "run_metadata": run_meta
    }
