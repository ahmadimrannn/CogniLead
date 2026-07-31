from textwrap import dedent
from graph.state import LeadState
from utils.crm_utils import ensure_company, ensure_contact, ensure_association, ensure_note, decide_route, build_note



def crm_writer(state: LeadState):
    """Takes the lead data and writes it to the CRM."""
    lead_id = state.get("lead_id")
    crm_retry_attempt = state.get("crm_retry_attempt", 0)

    lead_score_and_reason = state.get("lead_score_and_reason", {}) or {}
    extracted_lead = state.get("extracted_lead", {}) or {}
    company_data = state.get("company_data", {}) or {}

    enrichment_status = company_data.get("enrichment_status")
    name_match_confidence = company_data.get("name_match_confidence")

    score = lead_score_and_reason.get("score", 0)
    reason = lead_score_and_reason.get("reason", "")

    email = state.get("email")
    firstname = extracted_lead.get("firstname") or "Not specified"
    lastname = extracted_lead.get("lastname") or ""
    company_name = extracted_lead.get("company_name")
    company_domain = company_data.get("website_domain")

    has_company = bool(company_name)

    note = build_note(score, reason, lead_id, has_company, enrichment_status, name_match_confidence)

    company_id = state.get("company_id")
    contact_id = state.get("contact_id")
    is_associated = state.get("associated", False)
    note_added = state.get("note_written", False)

    try:
        company_id = ensure_company(company_id, has_company, company_name, company_domain)
        contact_id = ensure_contact(contact_id, firstname, lastname, email)
        is_associated = ensure_association(is_associated, has_company, contact_id, company_id)
        note_added = ensure_note(note_added, is_associated, contact_id, company_id, note)
        crm_write_status = "succeeded" if (is_associated and note_added) else "failed"
    except Exception as e:
        print(f"Failed to write in CRM. Error: {str(e)}")
        crm_write_status = "failed"

    route = decide_route(crm_write_status, crm_retry_attempt)

    return {
        "crm_write_status": crm_write_status,
        "contact_id": contact_id,
        "company_id": company_id,
        "associated": is_associated,
        "note_written": note_added,
        "note": note,
        "route": route,
    }