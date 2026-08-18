from pathlib import Path
import sys

# Add src/cognilead/ to sys.path so 'graph' and other modules resolve
cognilead_dir = Path(__file__).resolve().parent.parent
if str(cognilead_dir) not in sys.path:
    sys.path.insert(0, str(cognilead_dir))

from fastapi import FastAPI, HTTPException, status, Query
from graph.graph_executor import execute_graph
from graph.resume_graph import resume_graph
from pydantic import BaseModel, Field
from database.utils.get_db import get_db_connection
from api.event_logger import log_event


app = FastAPI(title="Lead Qualification API")

class LeadProcessRequest(BaseModel):
  lead_text: str = Field(
    ..., 
    min_length=1, 
    description="Raw lead communication text to process",
    examples=["We're a 40-person Series A fintech... can we get a demo?"]
  )
  email: str

class ResumeRequest(BaseModel):
  thread_id: str
  action: str

class FailedLeadRequest(BaseModel):
  limit: int = Query(default=50, ge=1, le=1000)


@app.post("/leads")
def process_leads(request: LeadProcessRequest):
  text = request.lead_text.strip()
  email = request.email.strip()
  
  if not text or not email.strip():
    raise HTTPException(
      status_code=status.HTTP_400_BAD_REQUEST, 
      detail="Can't process the lead without the lead details and the email."
    )

  try:
    response = execute_graph(text, email)
    return response
  except Exception as e:
    log_event(
      service="cognilead", event_type="api_exception", severity="error",
      node_or_route="/leads", message=str(e),
      context={"lead_text_len": len(text), "email": email},
    )
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
    )

    return result

  except Exception as e:
    log_event(
      service="cognilead", event_type="api_exception", severity="error",
      node_or_route="/leads/resume", message=str(e),
      context={"thread_id": request.thread_id, "action": request.action},
    )
    raise HTTPException(
      status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
      detail=f"Can't fetch results. {str(e)}"
    )



@app.get("/leads/failed")
def get_failed_leads(request: FailedLeadRequest):
  """
  Retrieves all lead records that ended up in 'failed_permanent' status.
  Direct SQL query against PostgreSQL checkpoints JSON data.
  """
  sql_query = """
    SELECT 
        thread_id,
        checkpoint->'channel_values'->>'lead_id' AS lead_id,
        checkpoint->'channel_values'->>'email' AS email,
        checkpoint->'channel_values'->>'crm_write_status' AS crm_write_status,
        checkpoint->'channel_values'->>'review_status_reason' AS failure_reason,
        checkpoint->>'ts' AS timestamp
    FROM checkpoints
    WHERE 
        checkpoint->'channel_values'->>'crm_write_status' = 'failed_permanent'
        OR checkpoint->'channel_values'->>'route' = 'failed_permanent'
    ORDER BY checkpoint->>'ts' DESC
    LIMIT %s;
  """

  try:
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(sql_query, (request.limit,))
            results = cursor.fetchall()

    failed_leads = [
      {
        "thread_id": row["lead_id"],
        "lead_id": row["lead_id"],
        "email": row["email"],
        "status": row["crm_write_status"] or "failed_permanent",
        "failure_reason": row["lead_score_and_reason"]['reason'],
      }
      for row in results
    ]

    return {
      "status": "success",
      "count": len(failed_leads),
      "failed_leads": failed_leads
    }

  except Exception as e:
    log_event(
      service="cognilead", event_type="api_exception", severity="error",
      node_or_route="/leads/failed", message=str(e),
      context={"limit": request.limit},
    )
    raise HTTPException(
      status_code=500, 
      detail=f"Database query failed: {str(e)}"
  )