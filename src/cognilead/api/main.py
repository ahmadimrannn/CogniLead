from fastapi import FastAPI, HTTPException, status
from graph.graph_executor import execute_graph
from pydantic import BaseModel, Field

app = FastAPI(title="Lead Qualification API")

class LeadProcessRequest(BaseModel):
  lead_text: str = Field(
    ..., 
    min_length=1, 
    description="Raw lead communication text to process",
    examples=["We're a 40-person Series A fintech... can we get a demo?"]
  )


@app.post("/leads")
def process_leads(request: LeadProcessRequest):
  text = request.lead_text.strip()
  if not text:
    raise HTTPException(
      status_code=status.HTTP_400_BAD_REQUEST, 
      detail="Can't process the lead without the lead details."
    )


  try:
    response = execute_graph(text)
    return response
  except Exception as e:
    print(str(e))
    raise HTTPException(
      status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
      detail=f"Failed to process the lead due to some internal error."
    )


