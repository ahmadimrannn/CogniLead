from langchain_google_genai import ChatGoogleGenerativeAI
from config.settings import LLM_MODEL_NAME
from graph.state import ExtractionNodeSchema, ScoringNodeSchema 
from dotenv import load_dotenv

load_dotenv()

llm = ChatGoogleGenerativeAI(
  model=LLM_MODEL_NAME
)

extractor_llm = llm.with_structured_output(ExtractionNodeSchema)
scorer_llm = llm.with_structured_output(ScoringNodeSchema)

