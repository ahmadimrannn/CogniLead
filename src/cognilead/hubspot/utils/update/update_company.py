from hubspot.config import headers
import requests

def update_company(company_id, company_name, company_domain):
  """Query HubSpot CRM to update company if the company already exists."""

  if not company_id or not company_name:
    print("Can't update company without these details. (company_id, company_name, company_description).")
    return None

  url = f"https://api.hubapi.com/crm/objects/2026-03/companies/{company_id}"

  payload = {
    "properties": {
      "name": company_name,
      "domain": company_domain
    }
  }

  try:
    response = requests.patch(url=url, headers=headers, json=payload, timeout=10)
    if response.status_code == 404:
      print("Failed to update the company.")
      return None

    response.raise_for_status()
    data = response.json()

    id = data.get("id")
    if id:
      return id

  except requests.exceptions.RequestException as e:
    print(f"HubSpot API Error while updating the company, Error: {str(e)}")
    return None
  
  
if __name__ == "__main__":
    pass
  