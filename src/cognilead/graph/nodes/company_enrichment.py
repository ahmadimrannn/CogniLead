from langchain_core.messages import HumanMessage, AIMessage
from graph.state import LeadState
from config.llm import company_enrichment_llm
from utils.web_search import search_web
from prompts.prompts import company_enrichment_node_prompt

def company_enrichment_node(state: LeadState):
  """In detail data extraction of the company."""

  extracted_lead_data = state.get('extracted_lead')
  company_name = extracted_lead_data.get('company_name', "")
  company_description = extracted_lead_data.get('company_description', '')

  search_results = search_web(company_name, company_description)
  
  prompt = company_enrichment_node_prompt(company_name, company_description, search_results)

  response = company_enrichment_llm.invoke([HumanMessage(content=prompt)])
  company_data = response.model_dump()

  if not company_data:
    return {
      "company_data": None
    }

  agent_message = f"""
    🌐 Company Enrichment Agent completed.

    Lead ID: {state['lead_id']}
    Target Company: {company_name or 'Unknown'}
    Enrichment Status: {company_data.get('enrichment_status')}
    Industry: {company_data.get('industry') or 'N/A'}

    Next -> Lead Scorer
    """

  return {
    "messages": [AIMessage(content=agent_message)],
    "company_data": company_data,
    "route": "lead_scorer"
  }