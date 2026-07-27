from graph.graph_builder import graph

def execute_graph(text: str):
  initial_state = {
    "text": text
  }
  response = graph.invoke(initial_state)
  return response


if __name__ == "__main__":
  execute_graph("yo man, i am a top level guy who runs the whole business of a fintech company (Bankly). around forty to 50 people work in my company. we want a sales lead qualifier.")