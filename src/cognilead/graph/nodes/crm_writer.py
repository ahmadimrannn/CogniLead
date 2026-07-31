from textwrap import dedent
from graph.state import LeadState
from config.settings import CRM_RETRY_ATTEMPT_LIMIT

from hubspot.utils.create_or_update.create_or_update_contact import create_or_update_contact
from hubspot.utils.create_or_update.create_or_update_company import create_or_update_company
from hubspot.utils.association.associate_contact_with_company import associate_contact_with_company
from hubspot.utils.write_note.write_note import write_note


def crm_writer(state: LeadState):
  """Takes the lead data and writes it to the CRM."""
  crm_retry_attempt = state.get("crm_retry_attempt", 0)
  lead_id = state.get("lead_id")

  lead_score_and_reason = state.get("lead_score_and_reason", {})
  extracted_lead = state.get("extracted_lead", {})
  company_data = state.get("company_data", {})

  enrichment_status = company_data.get("enrichment_status") if company_data else None
  name_match_confidence = company_data.get("name_match_confidence") if company_data else None

  score = lead_score_and_reason.get("score") if lead_score_and_reason else 0
  reason = lead_score_and_reason.get("reason") if lead_score_and_reason else ""

  email = state.get("email")
  firstname = extracted_lead.get("firstname") if extracted_lead else "Not specified"
  lastname = extracted_lead.get("lastname") if extracted_lead else ""
  company_name = extracted_lead.get("company_name") if extracted_lead else ""
  company_domain = company_data.get("website_domain") if company_data else ""

  warning = ""
  if enrichment_status in ("MISMATCH", "FAILED") and name_match_confidence in ("uncertain", "contradicted"):
      warning = "NOTE: Company data below is self-reported only — automated enrichment was disregarded due to unresolved company identity.\n"

  note = dedent(f"""\
      {warning}Lead Score: {score}
      Reason: {reason}
      Lead ID: {lead_id}""").strip()

  # Pre-declare variables to prevent UnboundLocalError on exception
  company_id = state.get("company_id")
  contact_id = state.get("contact_id")
  is_associated = state.get("associated", False)
  note_added = state.get("note_written", False)
  crm_write_status = "failed"

  try:
      if not company_id:
          company_id = create_or_update_company(company_name, company_domain)
      
      if not contact_id:
          contact_id = create_or_update_contact(firstname, lastname, email)

      if company_id and contact_id:
          if not is_associated:
              is_associated = associate_contact_with_company(contact_id, company_id)
          
          if is_associated and not note_added:
              note_added = write_note(contact_id, company_id, note)

          if is_associated and note_added:
              crm_write_status = "succeeded"

  except Exception as e:
      print(f"Failed to write in CRM. Error: {str(e)}")
      crm_write_status = "failed"

  # Routing logic
  if crm_write_status == "failed" and crm_retry_attempt < CRM_RETRY_ATTEMPT_LIMIT:
      route = "crm_retrier"
  elif crm_write_status == "failed":
      crm_write_status = "permanent_failed"
      route = "end"
  else:
      route = "end"

  return {
      "crm_write_status": crm_write_status,
      "contact_id": contact_id,
      "company_id": company_id,
      "associated": is_associated,
      "note_written": note_added,
      "note": note,
      "route": route,
  }