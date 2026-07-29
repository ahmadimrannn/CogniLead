from graph.state import LeadState
from config.llm import extractor_llm
from langchain_core.messages import HumanMessage, AIMessage
from prompts.prompts import lead_extractor_prompt
import uuid

def lead_extractor(state: LeadState):
  """Takes messy text and then extracts lead data from it"""

  data = state['text']
  email = state['email']
  prompt = lead_extractor_prompt(data)

  lead_id = str(uuid.uuid4())

  response = extractor_llm.invoke([HumanMessage(content=prompt)])
  extracted_lead = response.model_dump()

  agent_message = f"""
    🔍 Lead Extractor Agent completed.

    Input Length: {len(state.get('text', ''))} characters
    Lead ID: {lead_id}

    Next -> Company Enricher
    """


  return {
    "messages": [AIMessage(content=agent_message)],
    "extracted_lead": extracted_lead,
    "lead_id": lead_id,
    "email": email,
    "route": "company_enrichment_node"
  }



if __name__ == "__main__":
  pass