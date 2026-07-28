from typing import Optional, TypedDict, Literal
from schemas.extraction_node_schema import ExtractionNodeSchema
from schemas.company_enrichment_node_schema import CompanyEnrichmentNodeSchema
from schemas.lead_scorer_schema import ScoringNodeSchema

class LeadState(TypedDict):
    text: str
    extracted_lead: Optional[ExtractionNodeSchema]
    company_data: Optional[CompanyEnrichmentNodeSchema]
    lead_score_and_reason: Optional[ScoringNodeSchema]
    review_gate_status: Optional[Literal["accept", "needs_human_review", "reject"]]
    review_status_reason: Optional[str]
    human_decision: Optional[str] = None
    route: str