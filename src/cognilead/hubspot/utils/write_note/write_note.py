import requests
from datetime import datetime, timezone
from hubspot.config import headers

def write_note(contact_id: str, company_id: str, note: str) -> bool:
  """Write note to the contact and company using contact and company id."""

  if not contact_id or not company_id or not note:
      print("⚠️ Cannot write note without contact_id, company_id, and note content.")
      return False

  now_utc = datetime.now(timezone.utc)
  formatted_timestamp = now_utc.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'

  url = "https://api.hubapi.com/crm/objects/2026-03/notes"

  payload = {
      "properties": {
          "hs_timestamp": formatted_timestamp,
          "hs_note_body": str(note)
      },
      "associations": [
          {
              "to": {"id": str(contact_id)},
              "types": [
                  {
                      "associationCategory": "HUBSPOT_DEFINED", 
                      "associationTypeId": 202 
                  }
              ]
          },
          {
              "to": {"id": str(company_id)},
              "types": [
                  {
                      "associationCategory": "HUBSPOT_DEFINED", 
                      "associationTypeId": 190 
                  }
              ]
          }
      ]
  }

  try:
      response = requests.post(url=url, json=payload, headers=headers, timeout=10)
      response.raise_for_status()

      print("✅ Note written successfully.")
      return True

  except requests.exceptions.RequestException as e:
      error_details = e.response.text if hasattr(e, 'response') and e.response is not None else str(e)
      print(f"⚠️ HubSpot API error while writing note: {error_details}")
      return False


if __name__ == "__main__":
  contact_id = "528396334782"
  company_id = "337354739438"
  note = "hello just testing"
  added = write_note(contact_id, company_id, note)

  if added:
    print('note added')
  else:
    print('failed to add note')
  

