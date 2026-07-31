from graph.state import LeadState
from config.settings import CRM_RETRY_ATTEMPT_LIMIT


def crm_retrier(state: LeadState):
  """Increments retry attempts and routes back to crm_writer."""
  crm_retry_attempt = state.get("crm_retry_attempt", 0) + 1

  if crm_retry_attempt > CRM_RETRY_ATTEMPT_LIMIT:
    return {
        "crm_retry_attempt": crm_retry_attempt,
        "crm_write_status": "permanent_failed",
        "route": "end"
    }

  return {
      "crm_retry_attempt": crm_retry_attempt,
      "route": "crm_writer"
  }