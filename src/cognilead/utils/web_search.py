from langchain_tavily import TavilySearch
from config.llm import llm
from dotenv import load_dotenv
from config.settings import TAVILY_MAX_RESULTS, TAVILY_SEARCH_SEPTH

load_dotenv()

def search_web(company_name: str, company_description: str):
    """Search about the company on the web on the basis of company_name and company_description"""

    tavily = TavilySearch(
      max_results=TAVILY_MAX_RESULTS, 
      search_depth=TAVILY_SEARCH_SEPTH,
    )
    
    query_parts = [p for p in [company_name, company_description] if p]
    query = " ".join(query_parts) + " company"

    search_results = tavily.invoke(query)
    return search_results


if __name__ == "__main__":
    search_web("Dezy Solutions", "a software and automation studio for businesses that keep patching the same problems with new tools.")
