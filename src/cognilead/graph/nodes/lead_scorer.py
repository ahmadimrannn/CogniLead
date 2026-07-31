from graph.state import LeadState
from config.llm import scorer_llm
from langchain_core.messages import HumanMessage, AIMessage
from prompts.prompts import lead_scorer_prompt

def lead_scorer(state: LeadState):
  """Takes structured lead information from lead_extractor, and company_enrichment_node and then scores the lead and gives the reason of that score"""

  extracted_lead = state.get('extracted_lead', '')
  extracted_company_data = state.get('company_data', '')

  prompt = lead_scorer_prompt(extracted_lead, extracted_company_data)
  
  response = scorer_llm.invoke([HumanMessage(content=prompt)])
  lead_score_and_reason = response.model_dump()

  agent_message = f"""
    📊 Lead Scorer Agent completed.

    Lead ID: {state['lead_id']}
    Assigned Score: {lead_score_and_reason['score']}/10
    Enrichment Signal Used: {extracted_company_data['enrichment_status']}
    Scoring Explanation: {lead_score_and_reason['reason']}

    Next -> Human Review Gate
  """

  if lead_score_and_reason:
    print("✅ Lead Score and Reason Completed.")
  else:
    print("❌ Lead Score and Reason Failed.")

  return {
    "messages": [agent_message],
    "lead_score_and_reason": lead_score_and_reason,
    "route": "human_review_gate"
  }