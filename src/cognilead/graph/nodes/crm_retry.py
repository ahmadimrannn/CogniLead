from graph.state import LeadState
from config.settings import CRM_RETRY_ATTEMPT_LIMIT
from api.event_logger import log_event


def crm_retrier(state: LeadState):
  """Increments retry attempts and routes back to crm_writer."""
  crm_retry_attempt = state.get("crm_retry_attempt", 0) + 1
  lead_id = state.get("lead_id")

  if crm_retry_attempt > CRM_RETRY_ATTEMPT_LIMIT:
    log_event(
      service="cognilead",
      event_type="crm_retry_limit_exceeded",
      severity="warning",
      node_or_route="crm_retry",
      thread_id=lead_id,
      message="CRM retry limit exceeded; stopping workflow.",
      context={"crm_retry_attempt": crm_retry_attempt, "crm_retry_limit": CRM_RETRY_ATTEMPT_LIMIT},
    )
    return {
        "crm_retry_attempt": crm_retry_attempt,
        "crm_write_status": "permanent_failed",
        "route": "end"
    }

  log_event(
    service="cognilead",
    event_type="crm_retry_triggered",
    severity="info",
    node_or_route="crm_retry",
    thread_id=lead_id,
    message="Retrying CRM write after a failed attempt.",
    context={"crm_retry_attempt": crm_retry_attempt, "crm_retry_limit": CRM_RETRY_ATTEMPT_LIMIT},
  )

  return {
      "crm_retry_attempt": crm_retry_attempt,
      "route": "crm_writer"
  }