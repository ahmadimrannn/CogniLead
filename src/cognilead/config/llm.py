from langchain_google_genai import ChatGoogleGenerativeAI
from config.settings import LLM_MODEL_NAME
from schemas.extraction_node_schema import ExtractionNodeSchema
from schemas.company_enrichment_node_schema import CompanyEnrichmentNodeSchema
from schemas.lead_scorer_schema import ScoringNodeSchema
from dotenv import load_dotenv

load_dotenv()

llm = ChatGoogleGenerativeAI(
  model=LLM_MODEL_NAME
)

extractor_llm = llm.with_structured_output(ExtractionNodeSchema)
scorer_llm = llm.with_structured_output(ScoringNodeSchema)
company_enrichment_llm = llm.with_structured_output(CompanyEnrichmentNodeSchema)

