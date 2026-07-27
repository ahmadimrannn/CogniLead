from langgraph.graph import StateGraph, START, END
from graph.state import LeadState

from graph.nodes.lead_extractor import lead_extractor
from graph.nodes.lead_scorer import lead_scorer

def build_graph():
  # Initializing the graph
  graph = StateGraph(LeadState)

  # Add nodes in the graph
  graph.add_node("lead_extractor", lead_extractor)
  graph.add_node("lead_scorer", lead_scorer)

  # Add edges in the graph to connect nodes or define the flow
  graph.add_edge(START, 'lead_extractor')
  graph.add_edge("lead_extractor", "lead_scorer")
  graph.add_edge("lead_scorer", END)

  final_graph = graph.compile()

  return final_graph


graph = build_graph()