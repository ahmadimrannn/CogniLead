from hubspot.config import headers
import requests

def search_company_by_name(company_name):
  """Query HubSpot's CRM to get company by company name.
  
    Returns:
      str: Company ID if found.
      None: If company does not exist or query fails.
  """

  if not company_name or not company_name.strip():
    return None

  url = f"https://api.hubapi.com/crm/objects/2026-03/companies/search"
  
  payload = {
    "filterGroups": [
        {
            "filters": [
                {
                    "propertyName": "name",
                    "operator": "EQ",
                    "value": company_name.strip()
                }
            ]
        }
    ],
  }

  try:
    response = requests.post(url=url, headers=headers, json=payload, timeout=10)

    if response.status_code == 404:
      return None

    response.raise_for_status()
    data = response.json()

    results = data.get("results", [])
    if results:
      company_id = results[0]['id']
      return company_id

  except requests.exceptions.RequestException as e:
    print(f"HubSpot API Error while searching for company by company name {company_name}, Error: {str(e)}")
    return None


if __name__ == "__main__":
  company_name = "CogniLead"
  company_id = search_company_by_name(company_name)

  if company_id:
    print(f"Company ID found. Company ID: {company_id}")
  else:
    print("Company ID not found.")


  