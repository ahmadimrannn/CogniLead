from hubspot.config import headers
import requests

def associate_contact_with_company(contact_id: str, company_id: str):
  """Associates an existing Contact with an existing Company in HubSpot.
    
    Uses the 2026-03 default association PUT endpoint.
    
    Returns:
        bool: True if successfully associated, False otherwise.
  """
  
  if not contact_id or not company_id:
    print(f"Can't do association without contact id and company id. Both ids are required in order to associate.")
    return False

  url = f"https://api.hubapi.com/crm/objects/2026-03/contacts/{contact_id}/associations/default/companies/{company_id}"

  try:
    response = requests.put(url=url, headers=headers, timeout=10)
    response.raise_for_status()

    print(f"Associated the contact of contact id ({contact_id}) with the company of company id ({company_id}).")
    return True

  except requests.exceptions.RequestException as e:
    print(f"HubSpot API error while associating the contact with company")
    return False