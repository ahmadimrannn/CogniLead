from hubspot.utils.search.search_contact_by_email import search_contact_by_email
from hubspot.utils.create.create_contact import create_contact
from hubspot.utils.update.update_contact import update_contact

def create_or_update_contact(firstname: str, lastname: str, email: str):
  """Query HubSpot's CRM to create or update contact.
  
    Returns:
      Created or updated contact status
  """

  if not email.strip():
    print("Can't create or update the contact without email. Please provide email.")
    return None

  contact_id = search_contact_by_email(email)
  if contact_id:
    print("contact already exists. updating it with new details")
    id = update_contact(contact_id, firstname, lastname, email)
    if id:
      print("Contact updated ✅")
      return id

  else:
    print("Creating the contact")
    id = create_contact(firstname, lastname, email)
    if id:
      print("Contact created ✅")
      return id


if __name__ == "__main__":
  firstname = "Shoaib"
  lastname = "Anwar"
  email = "shoaibanwar@gmail.com"

  result = create_or_update_contact(firstname, lastname, email)
  print(result)


  