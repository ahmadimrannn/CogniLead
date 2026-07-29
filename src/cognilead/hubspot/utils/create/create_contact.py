from hubspot.config import headers
import requests

def create_contact(firstname, lastname, email):
  """Query HubSpot CRM to create contact."""

  if not email:
    print("Can't create the contact without details. Please provide the firstname, lastname, and email.")
    return None

  url = f"https://api.hubapi.com/crm/v3/objects/contacts"

  payload = {
    "properties": {
      "firstname": firstname,
      "lastname": lastname,
      "email": email
    }
  }

  try:
    response = requests.post(url=url, headers=headers, json=payload, timeout=10)
    if response.status_code == 404:
      print(f"Failed to create the contact.")
      return None

    response.raise_for_status()
    data = response.json()

    id = data.get("id")
    if id:
      return id

  except requests.exceptions.RequestException as e:
    print(f"HubSpot API Error while creating the contact, Error: {str(e)}")
    return None


if __name__ == "__main__":
  firstname = "james"
  lastname = 'bond'
  email = "jamesbond@gmail.com"

  result = create_contact(firstname, lastname, email)
  print(result)

