import os

from langgraph.graph import StateGraph, START, END
from graph.state import LeadState

from graph.nodes.lead_extractor import lead_extractor
from graph.nodes.company_enrichment import company_enrichment_node
from graph.nodes.lead_scorer import lead_scorer
from graph.nodes.human_review_gate import human_review_gate 
from graph.nodes.crm_writer import crm_writer

from langgraph.checkpoint.memory import MemorySaver

from utils.router import select_route

# Register custom Pydantic schema classes for MsgPack deserialization
os.environ["LANGGRAPH_ALLOWED_MSGPACK_MODULES"] = (
    "schemas.extraction_node_schema:ExtractionNodeSchema,"
    "schemas.company_enrichment_node_schema:CompanyEnrichmentNodeSchema,"
    "schemas.lead_scorer_schema:ScoringNodeSchema"
)

def build_graph():
  # Initializing the graph
  graph = StateGraph(LeadState)

  memory = MemorySaver()

  # Add nodes in the graph
  graph.add_node("lead_extractor", lead_extractor)
  graph.add_node("company_enrichment_node", company_enrichment_node)
  graph.add_node("lead_scorer", lead_scorer)
  graph.add_node("human_review_gate", human_review_gate)
  graph.add_node("crm_writer", crm_writer)

  # Add edges in the graph to connect nodes or define the flow
  graph.add_edge(START, "lead_extractor")
  graph.add_edge("lead_extractor", "company_enrichment_node")
  graph.add_edge("company_enrichment_node", "lead_scorer")
  graph.add_edge("lead_scorer", "human_review_gate")
  graph.add_conditional_edges(
    "human_review_gate",
    select_route,
    {
      "crm_writer": "crm_writer",
      "end": END
    }
  )
  graph.add_edge("crm_writer", END)

  final_graph = graph.compile(checkpointer=memory)

  return final_graph


graph = build_graph()