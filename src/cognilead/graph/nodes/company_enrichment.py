from langchain_core.messages import HumanMessage
from graph.state import LeadState
from config.llm import company_enrichment_llm
from utils.web_search import search_web
from prompts.prompts import company_enrichment_node_prompt

def company_enrichment_node(state: LeadState):
  """In detail data extraction of the company."""

  extracted_lead_data = state.get('extracted_lead')
  company_name = extracted_lead_data.company_name
  company_description = extracted_lead_data.company_description

  search_results = search_web(company_name, company_description)
  
  prompt = company_enrichment_node_prompt(company_name, company_description, search_results)

  company_data = company_enrichment_llm.invoke([HumanMessage(content=prompt)])

  if not company_data:
    return {
      "company_data": None
    }

  return {
    "company_data": company_data
  }