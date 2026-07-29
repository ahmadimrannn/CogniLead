from hubspot.config import headers
import requests

def create_company(company_name, company_domain):
  """Query HubSpot CRM to create company."""

  if not company_name:
    print("Can't update company without these details. (company_id, company_name, company_description).")
    return None

  url = f"https://api.hubapi.com/crm/objects/2026-03/companies"

  payload = {
    "properties": {
      "name": company_name,
      "domain": company_domain
    }
  }

  try:
    response = requests.post(url=url, headers=headers, json=payload, timeout=10)
    if response.status_code == 404:
      print(f"Failed to create the company.")
      return None

    response.raise_for_status()
    data = response.json()

    id = data.get("id")
    if id:
      return id

  except requests.exceptions.RequestException as e:
    print(f"HubSpot API Error while creating the company, Error: {str(e)}")
    return None
  
  
if __name__ == "__main__":
    pass