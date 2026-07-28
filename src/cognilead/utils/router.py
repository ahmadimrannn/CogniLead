from graph.state import LeadState

def select_route(state: LeadState):
  """Select the routes on the basis of the route variable in the state"""

  route = state.get("route", "")
  return route