from graph.graph_builder import graph

def execute_graph(text: str):
  initial_state = {
    "text": text
  }
  response = graph.invoke(initial_state)
  return response

if __name__ == "__main__":
  response = execute_graph("I run a 10-person logistics startup, we need help qualifying inbound freight leads")

  print(response)