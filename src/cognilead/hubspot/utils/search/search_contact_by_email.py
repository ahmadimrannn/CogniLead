from hubspot.config import headers
import requests

def search_contact_by_email(email: str):
  """Query HubSpot's CRM to get contacts by emails.

  Returns:
    str: Contact ID if found.
    None: If contact does not exist or query fails.
  """

  if not email or not email.strip().lower():
    return None

  url = f"https://api.hubapi.com/crm/objects/2026-03/contacts/search"

  payload = {
    "filterGroups": [
        {
            "filters": [
                {
                    "propertyName": "email",
                    "operator": "EQ",
                    "value": email.strip().lower()
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

    results = data.get('results', [])
    if results:
      contact_id = results[0]["id"]
      return contact_id

  except requests.exceptions.RequestException as e:
    print(f"HubSpot API error while searching email {email}, Error: {str(e)}")
    return None


if __name__ == "__main__":
  contact_email = "testlead@example.com"

  contact_id = search_contact_by_email(contact_email)

  if contact_id:
    print(f"Contact ID found. Contact ID: {contact_id}")
  else:
    print(f"Contact ID not found. Contact ID: {contact_id}")
