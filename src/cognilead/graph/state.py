from typing import Optional, TypedDict
from schemas.extraction_node_schema import ExtractionNodeSchema
from schemas.company_enrichment_node_schema import CompanyEnrichmentNodeSchema
from schemas.lead_scorer_schema import ScoringNodeSchema

class LeadState(TypedDict):
    text: str
    extracted_lead: Optional[ExtractionNodeSchema]
    company_data: Optional[CompanyEnrichmentNodeSchema]
    lead_score_and_reason: Optional[ScoringNodeSchema]