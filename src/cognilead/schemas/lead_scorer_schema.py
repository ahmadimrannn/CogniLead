from pydantic import BaseModel, Field

class ScoringNodeSchema(BaseModel):
    score: int = Field(description="Score of the lead from 1 to 10 based on intent and fit")
    reason: str = Field(description="Clear explanation for the assigned score")