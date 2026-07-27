from graph.state import LeadState
from config.llm import scorer_llm
from langchain_core.messages import HumanMessage

def lead_scorer(state: LeadState):
  """Takes structured lead information from lead_extractor and then scores the lead and gives the reason of that score"""

  extracted_lead = state['extracted_lead']
  prompt = f"""You are an expert B2B Lead Qualification Specialist. Evaluate the following extracted lead information, assign a qualification score from 1 to 10, and provide a clear justification.

  ### Evaluation Criteria:
  1. Decision-Maker Authority: High score for executive, ownership, or buying roles (e.g., Founder, CEO, Head of, Director, VP, "runs"/"founded" a company). Low score for non-decision makers (e.g., student, intern, individual contributor) or missing role/ownership signal entirely.
  2. Company Presence: Score based on information richness, not naming alone. A named company scores highest, but a clear company description (size, industry, funding stage) without a proper name should still score as partial-to-good — do not treat an unnamed-but-described company the same as no company information at all.
  3. Stated Need & Intent: High score for specific, actionable problems with clear intent (e.g., requesting a demo, seeking automation).

  ### Explicitly Ignore:
  - Grammar, spelling, capitalization, and message formality. A messy, lowercase, abbreviation-heavy message from a real decision-maker must score the same as a polished one stating identical facts. Never let writing style influence the score in either direction.

  ### Scoring Matrix:
  - 8–10 (High Quality): Clear decision-maker/owner + company identified (named or well-described) + explicit, actionable intent.
  - 5–7 (Medium Quality): Partial information (e.g., explicit need, but vague role or company details).
  - 1–4 (Low Quality / Unqualified): Non-business roles (e.g., student/intern), missing all critical info, or vague/irrelevant needs.

  ### Extracted Lead Data to Evaluate:
  {extracted_lead}

  Evaluate the lead data above, assign an integer score (1–10), and write a concise 1–2 sentence explanation for your decision."""

  response = scorer_llm.invoke([HumanMessage(content=prompt)])

  return {
    "lead_score_and_reason": response
  }