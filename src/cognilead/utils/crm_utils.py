from config.settings import CRM_RETRY_ATTEMPT_LIMIT

from hubspot.utils.create_or_update.create_or_update_contact import create_or_update_contact
from hubspot.utils.create_or_update.create_or_update_company import create_or_update_company
from hubspot.utils.association.associate_contact_with_company import associate_contact_with_company
from hubspot.utils.write_note.write_note import write_note

def ensure_company(company_id, has_company, company_name, company_domain):
    if company_id or not has_company:
        return company_id
    return create_or_update_company(company_name, company_domain)


def ensure_contact(contact_id, firstname, lastname, email):
    if contact_id:
        return contact_id
    return create_or_update_contact(firstname, lastname, email)


def ensure_association(is_associated, has_company, contact_id, company_id):
    if is_associated or not has_company:
        return True  # already done, or nothing to associate
    return associate_contact_with_company(contact_id, company_id)


def ensure_note(note_added, is_associated, contact_id, company_id, note):
    if note_added or not is_associated:
        return note_added
    return write_note(contact_id, note, company_id)  # write_note itself should skip the company-note call when company_id is None


def decide_route(crm_write_status, crm_retry_attempt):
    if crm_write_status == "succeeded":
        return "end"
    if crm_retry_attempt < CRM_RETRY_ATTEMPT_LIMIT:
        return "crm_retrier"
    return "end"


def build_note(score, reason, lead_id, has_company, enrichment_status, name_match_confidence):
    lines = []
    if not has_company:
        lines.append("NOTE: No company name was stated in the original lead — this contact was created without a company association.")
    if enrichment_status == "MISMATCH" or name_match_confidence in ("uncertain", "contradicted"):
        lines.append("NOTE: Company data below is self-reported only — automated enrichment was disregarded due to unresolved company identity.")
    lines.append(f"Lead Score: {score}")
    lines.append(f"Reason: {reason}")
    lines.append(f"Lead ID: {lead_id}")
    return "\n".join(lines)