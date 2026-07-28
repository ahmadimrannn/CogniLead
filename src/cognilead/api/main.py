from fastapi import FastAPI, HTTPException, status
from graph.graph_executor import execute_graph
from graph.resume_graph import resume_graph
from pydantic import BaseModel, Field
import uuid

app = FastAPI(title="Lead Qualification API")

class LeadProcessRequest(BaseModel):
  lead_text: str = Field(
    ..., 
    min_length=1, 
    description="Raw lead communication text to process",
    examples=["We're a 40-person Series A fintech... can we get a demo?"]
  )

class ResumeRequest(BaseModel):
  thread_id: str
  action: str


@app.post("/leads")
def process_leads(request: LeadProcessRequest):
  text = request.lead_text.strip()
  if not text:
    raise HTTPException(
      status_code=status.HTTP_400_BAD_REQUEST, 
      detail="Can't process the lead without the lead details."
    )

  thread_id = str(uuid.uuid4())
  try:
    response = execute_graph(text, thread_id)
    return response
  except Exception as e:
    print(str(e))
    raise HTTPException(
      status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
      detail=f"Failed to process the lead due to some internal error."
    )


@app.post("/leads/resume")
def resume_workflow(request: ResumeRequest):
  
  if request.action not in {"approve", "reject"}:
    raise HTTPException(
      status_code=status.HTTP_400_BAD_REQUEST,
      detail="Invalid Action"
    )
  

  try:
    result = resume_graph(
      action=request.action,
      thread_id=request.thread_id,
      edited_query=request.edited_query
    )

    return result

  except Exception as e:
    print(str(e))
    raise HTTPException(
      status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
      detail=f"Can't fetch results."
    )
  
  

