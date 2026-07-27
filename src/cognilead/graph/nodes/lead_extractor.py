from graph.state import LeadState
from config.llm import extractor_llm
from langchain_core.messages import HumanMessage
from prompts.prompts import lead_extractor_prompt

def lead_extractor(state: LeadState):
  """Takes messy text and then extracts lead data from it"""

  data = state['text']
  prompt = lead_extractor_prompt(data)

  response = extractor_llm.invoke([HumanMessage(content=prompt)])

  return {
    "extracted_lead": response
  }



if __name__ == "__main__":
  pass