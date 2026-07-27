from pydantic import BaseModel, Field
from typing import Optional

class ExtractionNodeSchema(BaseModel):
    name: Optional[str] = Field(default=None, description="Name of the lead, or null if missing")
    company_name: Optional[str] = Field(default=None, description="Company name, or null if missing")
    company_description: Optional[str] = Field(default=None, description="Company description according to the given context.")
    role: Optional[str] = Field(default=None, description="Role/job title of the lead, or null if missing")
    stated_need: Optional[str] = Field(default=None, description="What the lead explicitly wants or needs")