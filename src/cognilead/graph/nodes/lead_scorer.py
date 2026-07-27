from graph.state import LeadState
from config.llm import scorer_llm
from langchain_core.messages import HumanMessage
from prompts.prompts import lead_scorer_prompt

def lead_scorer(state: LeadState):
  """Takes structured lead information from lead_extractor, and company_enrichment_node and then scores the lead and gives the reason of that score"""

  extracted_lead = state.get('extracted_lead', '')
  extracted_company_data = state.get('company_data', '')

  prompt = lead_scorer_prompt(extracted_lead, extracted_company_data)
  
  response = scorer_llm.invoke([HumanMessage(content=prompt)])

  return {
    "lead_score_and_reason": response
  }