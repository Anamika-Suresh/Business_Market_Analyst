import operator
from typing import Annotated, Any, Dict, List, Optional
from typing_extensions import TypedDict

from schemas.company import CompanyProfile
from schemas.competitor import CompetitorAnalysis
from schemas.news import NewsAndHiring
from schemas.risk import RiskFindings
from schemas.evidence import EvidenceRecord, ValidationIssue
from schemas.report import ResearchBrief, CompanyIntelligenceReport

class GraphState(TypedDict, total=False):
    """LangGraph typed state for MarketMind AI multi-agent workflow."""
    # Input parameters
    company_name: str
    company_url: Optional[str]
    lookback_days: int
    user_priorities: Optional[str]
    
    # Supervisor outputs
    research_brief: Optional[ResearchBrief]
    
    # Distinct outputs from the four parallel specialist agents
    company_profile: Optional[CompanyProfile]
    competitor_analysis: Optional[CompetitorAnalysis]
    news_and_hiring: Optional[NewsAndHiring]
    risk_findings: Optional[RiskFindings]
    
    # Reducer-managed lists that safely merge during parallel fan-in
    evidence_records: Annotated[List[EvidenceRecord], operator.add]
    validation_issues: Annotated[List[ValidationIssue], operator.add]
    errors: Annotated[List[str], operator.add]
    
    # Synthesis & final outputs
    final_report: Optional[CompanyIntelligenceReport]
    run_metadata: Dict[str, Any]
