from hubspot.config import headers
import requests

def update_contact(contact_id, firstname, lastname, email):
  """Query HubSpot CRM to update contact if the contact already exists."""

  if not contact_id:
    print("Can't update the contact without contact id. Please provide the contact id")
    return None

  url = f"https://api.hubapi.com/crm/v3/objects/contacts/{contact_id}"

  payload = {
    "properties": {
      "firstname": firstname,
      "lastname": lastname,
      "email": email
    }
  }

  try:
    response = requests.patch(url=url, headers=headers, json=payload, timeout=10)
    if response.status_code == 404:
      print(f"Failed to update the contact.")
      return None

    response.raise_for_status()
    data = response.json()

    id = data.get("id")
    if id:
      return id

  except requests.exceptions.RequestException as e:
    print(f"HubSpot API Error while updating the contact, Error: {str(e)}")
    return None


if __name__ == "__main__":
  firstname = "ahmad"
  lastname = 'imran'
  email = "ahmad123@gmail.com"
  contact_id = 525299460854

  result = update_contact(contact_id, firstname, lastname, email)
  print(result)

