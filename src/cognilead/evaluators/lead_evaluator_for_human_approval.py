from typing import Literal
from graph.state import LeadState

def evaluate_lead(state: LeadState):
    """Evaluate the lead on the basis of Company Enrichment Node and Lead Scorer."""

    enrichment_data = state.get('company_data')
    lead_score_data = state.get('lead_score_and_reason')

    # Safe extraction with fallback defaults
    score = lead_score_data.get('score') if lead_score_data else 0
    enrichment_status = enrichment_data.get('enrichment_status') if enrichment_data else "NOT_FOUND"
    name_match_confidence = enrichment_data.get("name_match_confidence") if enrichment_data else None

    # 1. Reject unqualified leads
    if score <= 3:
        return "reject", f"""The lead is auto rejected as the score is less than or equal to 3.

        - Score: {score}/10 
        - Enrichment Status: {enrichment_status} 
        - Name Match Confidence: {name_match_confidence} 
        """

    # 2. Auto-accept high score leads with valid enrichment/confidence
    is_high_score = score >= 8
    is_good_match = (
        enrichment_status == "SUCCESS" or 
        name_match_confidence in ["exact", "plausible_variant"]
    )

    if is_high_score and is_good_match:
        return "accept", f"""The lead is auto accepted as the lead has high score and has a good match.

        - Score: {score}/10 
        - Enrichment Status: {enrichment_status} 
        - Name Match Confidence: {name_match_confidence} 
        """

    # 3. Everything else requires human review
    return "needs_human_review", f"""The lead required human approval as the lead is ambiguous. 

    - Score: {score}/10 
    - Enrichment Status: {enrichment_status} 
    - Name Match Confidence: {name_match_confidence} 
"""