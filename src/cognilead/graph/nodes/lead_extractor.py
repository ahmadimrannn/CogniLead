from graph.state import LeadState
from config.llm import extractor_llm
from langchain_core.messages import HumanMessage

def lead_extractor(state: LeadState):
  """Takes messy text and then extracts lead data from it"""

  data = state['text']
  prompt = f"""You are a senior B2B Lead Intelligence Extractor. Analyze the following inbound text and extract structured lead information.

  ### Rules:
  1. Strict Grounding: Extract ONLY facts explicitly stated in the text. Do NOT invent, assume, or extrapolate data.
  2. Missing Information: If a field is not directly mentioned, leave it empty/null. Never use filler placeholders like "N/A", "Unknown", or "Not provided".
  3. Role Inference: Infer decision-making authority from context, not just explicit titles. Phrases like "I run", "I founded", "my company", "we built" indicate ownership/founder-level authority even without a stated title. Only leave role null if there is truly no ownership or positional signal at all.
  4. Company Name vs Description: If a proper company name is stated, extract it as company_name. If the text describes the company without naming it (e.g. "a 40-person fintech", "a small consulting shop"), extract that description into company_description instead of leaving both fields null. Only leave both null if the text gives no company information whatsoever.
  5. Stated Need: Summarize their primary request, goal, or problem into a concise, action-oriented statement.

  ### Inbound Text to Extract From:
  {data}

  Extract and map the lead details (name, role, company_name, company_description, stated_need) from the text above."""

  response = extractor_llm.invoke([HumanMessage(content=prompt)])

  return {
    "extracted_lead": response
  }



if __name__ == "__main__":
  pass