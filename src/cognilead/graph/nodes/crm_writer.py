from langchain_core.messages import AIMessage
from graph.state import LeadState

from hubspot.utils.create_or_update.create_or_update_contact import create_or_update_contact
from hubspot.utils.create_or_update.create_or_update_company import create_or_update_company

from hubspot.utils.association.associate_contact_with_company import associate_contact_with_company

from hubspot.utils.write_note.write_note import write_note

def crm_writer(state: LeadState):
  """Takes the lead data and writes it to the CRM."""

  lead_id = state.get("lead_id")

  lead_score_and_reason = state.get('lead_score_and_reason', {})
  extracted_lead = state.get("extracted_lead", {})
  company_data = state.get("company_data", {})

  score = lead_score_and_reason.get('score') if lead_score_and_reason else 0
  reason = lead_score_and_reason.get('reason') if lead_score_and_reason else ""


  email = state.get('email')
  firstname = extracted_lead.get('firstname') if extracted_lead else "Not specified"
  lastname = extracted_lead.get('lastname') if extracted_lead else ""
  company_name = extracted_lead.get('company_name') if extracted_lead else ""
  company_domain = company_data.get("website_domain") if company_data else ""

  note = f"""
    Lead ID: {lead_id}
    Lead Score: {score}
    Reason: {reason}
  """

  crm_write_status = state.get('crm_write_status', '')

  try:
    company_id = create_or_update_company(company_name, company_domain)
    contact_id = create_or_update_contact(firstname, lastname, email)
    if company_id and contact_id:
      is_associated = associate_contact_with_company(contact_id, company_id)
      note_added = write_note(contact_id, company_id, note)

      if is_associated and note_added:
        crm_write_status = "succeeded"
      else:
        crm_write_status = "failed"
  except Exception as e:
    print(f"Failed to write in CRM. Error: {str(e)}")
    crm_write_status = "failed"

  return {
    "crm_write_status": crm_write_status
  }
    
  



