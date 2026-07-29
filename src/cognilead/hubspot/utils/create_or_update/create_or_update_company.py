from hubspot.utils.search.search_company_by_name import search_company_by_name
from hubspot.utils.create.create_company import create_company 
from hubspot.utils.update.update_company import update_company

def create_or_update_company(company_name: str, company_domain: str):
  """Query HubSpot's CRM to create or update company.
  
    Returns:
      Created or updated company id
  """

  if not company_name.strip():
    print("Can't create or update the company without company name. Please provide these details.")
    return None

  company_id = search_company_by_name(company_name)
  if company_id:
    print("company already exists. updating it with new details")
    id = update_company(company_id, company_name, company_domain)
    if id:
      print("Company updated ✅")
      return id

  else:
    print("Creating the company")
    id = create_company(company_name, company_domain)
    if id:
      print("Company Created ✅")
      return id


if __name__ == "__main__":
  company_name = "Captur"
  company_domain = "captur.com"

  result = create_or_update_company(company_name, company_domain)
  print(result)


  