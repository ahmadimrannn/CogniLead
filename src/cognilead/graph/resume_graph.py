from graph.graph_builder import graph
from langgraph.types import Command

def resume_graph(
    action: str,
    thread_id: str
):

  config = {
    "configurable": {
      "thread_id": thread_id
    }
  }

  payload = {
    "action": action
  }

  response = graph.invoke(
    Command(resume=payload),
    config=config
  )

  if "__interrupt__" in response:
    return {
      "status": "interrupted",
      "interrupt": response['__interrupt__'][0].value,
      "thread_id": thread_id
    }
    
  return {
    "status": "completed",
    **response
  }

