from graph.state import LeadState
from langgraph.types import interrupt
from evaluators.lead_evaluator_for_human_approval import evaluate_lead

def process_interrupt(state: LeadState):
    extracted_lead = state.get("extracted_lead")
    score_data = state.get("lead_score_and_reason")
    company_data = state.get("company_data")
    review_status_reason = state.get("review_status_reason")

    lead_dict = extracted_lead.model_dump() if hasattr(extracted_lead, "model_dump") else extracted_lead
    company_dict = company_data.model_dump() if hasattr(company_data, "model_dump") else company_data

    score = score_data.get('score', 0) if score_data else "N/A"
    reason = score_data.get('reason', "") if score_data else "No score reason provided."

    approval = interrupt(
        {
            "type": "lead_approval",
            "lead_data": lead_dict,
            "company_data": company_dict,
            "score": score,
            "reason": reason,
            "review_status_reason": review_status_reason,
            "message": f"Human review required (Score: {score}/10). Reason: {reason}"
        }
    )

    # Safely handle either dictionary or string payload returned upon resumption
    if isinstance(approval, dict):
        return approval.get("action")
    return approval

def human_review_gate(state: LeadState):
    """Asks for human review in ambiguous cases or routes accepted/rejected leads."""

    review_gate_status, review_status_reason = evaluate_lead(state)

    if review_gate_status == "accept":
        human_action = None
        route = "end" # Will update to 'crm_writer' in next phase
    elif review_gate_status == "needs_human_review":
        human_action = process_interrupt(state)
        if human_action == "approve":
            route = "end" # Will update to 'crm_writer' in next phase
        else:
            route = "end"
    else: 
        route = "end"
        human_action = None

    return {
        "review_gate_status": review_gate_status,
        "review_status_reason": review_status_reason,
        "human_decision": human_action,
        "route": route
    }