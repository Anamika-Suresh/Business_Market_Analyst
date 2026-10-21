import logging
from langgraph.graph import StateGraph, START, END

from state import GraphState
from nodes.supervisor import supervisor_node
from nodes.evidence_validation import evidence_validation_node
from nodes.report_generator import report_generator_node
from agents.company_profile import company_profile_agent
from agents.competitor_intelligence import competitor_intelligence_agent
from agents.news_hiring import news_hiring_agent
from agents.risk_intelligence import risk_intelligence_agent

logger = logging.getLogger(__name__)

def build_graph() -> StateGraph:
    """Build and compile the multi-agent MarketMind AI StateGraph.
    
    Architecture:
    START -> supervisor -> [fan-out to 4 parallel agents]
        ├── company_profile
        ├── competitor_intelligence
        ├── news_hiring
        └── risk_intelligence
    [fan-in join] -> evidence_validation -> report_generator -> END
    """
    workflow = StateGraph(GraphState)

    # 1. Add workflow nodes
    workflow.add_node("supervisor", supervisor_node)
    workflow.add_node("company_profile", company_profile_agent)
    workflow.add_node("competitor_intelligence", competitor_intelligence_agent)
    workflow.add_node("news_hiring", news_hiring_agent)
    workflow.add_node("risk_intelligence", risk_intelligence_agent)
    workflow.add_node("evidence_validation", evidence_validation_node)
    workflow.add_node("report_generator", report_generator_node)

    # 2. Add entry edge
    workflow.add_edge(START, "supervisor")

    # 3. Explicit fan-out from supervisor to 4 parallel specialist agents
    workflow.add_edge("supervisor", "company_profile")
    workflow.add_edge("supervisor", "competitor_intelligence")
    workflow.add_edge("supervisor", "news_hiring")
    workflow.add_edge("supervisor", "risk_intelligence")

    # 4. Explicit fan-in join: all 4 parallel agents converge into evidence_validation
    workflow.add_edge("company_profile", "evidence_validation")
    workflow.add_edge("competitor_intelligence", "evidence_validation")
    workflow.add_edge("news_hiring", "evidence_validation")
    workflow.add_edge("risk_intelligence", "evidence_validation")

    # 5. Synthesis and report generation edges
    workflow.add_edge("evidence_validation", "report_generator")
    workflow.add_edge("report_generator", END)

    return workflow

def get_compiled_graph():
    """Return compiled executable LangGraph instance."""
    workflow = build_graph()
    return workflow.compile()
