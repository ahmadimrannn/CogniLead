from graph.state import LeadState
from config.llm import extractor_llm
from langchain_core.messages import HumanMessage, AIMessage
from prompts.prompts import lead_extractor_prompt
from api.event_logger import log_event


def lead_extractor(state: LeadState):
  """Takes messy text and then extracts lead data from it"""

  data = state.get("text")
  lead_id = state.get("lead_id")
  email = state.get('email')
  prompt = lead_extractor_prompt(data)

  log_event(
    service="cognilead",
    event_type="lead_extractor_started",
    severity="info",
    node_or_route="lead_extractor",
    thread_id=lead_id,
    message="Lead extraction started.",
    context={"lead_text_length": len(data), "email": email},
  )

  try:
    response = extractor_llm.invoke([HumanMessage(content=prompt)])
    extracted_lead = response.model_dump()
  except Exception as exc:
    log_event(
      service="cognilead",
      event_type="lead_extraction_exception",
      severity="critical",
      node_or_route="lead_extractor",
      thread_id=lead_id,
      message=str(exc),
      context={"lead_text_length": len(data), "email": email},
    )
    raise

  agent_message = f"""
    🔍 Lead Extractor Agent completed.

    Input Length: {len(state.get('text', ''))} characters
    Lead ID: {lead_id}

    Next -> Company Enricher
    """

  if extracted_lead:
    log_event(
      service="cognilead",
      event_type="lead_extractor_completed",
      severity="info",
      node_or_route="lead_extractor",
      thread_id=lead_id,
      message="Lead extraction completed successfully.",
      context={"lead_text_length": len(data), "email": email, "keys": list(extracted_lead.keys())[:10]},
    )
    print("✅ Lead Extraction Completed.")
  else:
    log_event(
      service="cognilead",
      event_type="lead_extraction_failure",
      severity="critical",
      node_or_route="lead_extractor",
      thread_id=lead_id,
      message="Lead extraction returned no usable data.",
      context={"lead_text_length": len(data), "email": email},
    )
    print("❌ Lead Extraction Failed.")

  return {
    "messages": [agent_message],
    "extracted_lead": extracted_lead,
    "email": email,
    "route": "company_enrichment_node"
  }



if __name__ == "__main__":
  pass