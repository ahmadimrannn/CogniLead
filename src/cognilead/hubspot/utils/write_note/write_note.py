import requests
from datetime import datetime, timezone
from hubspot.config import headers

def write_note(contact_id: str, note: str, company_id: str = None) -> bool:
  """Write note to the contact, and to the company too if company_id is given."""

  if not contact_id or not note:
      print("⚠️ Cannot write note without contact_id and note content.")
      return False

  now_utc = datetime.now(timezone.utc)
  formatted_timestamp = now_utc.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'

  url = "https://api.hubapi.com/crm/objects/2026-03/notes"

  associations = [
      {
          "to": {"id": str(contact_id)},
          "types": [
              {"associationCategory": "HUBSPOT_DEFINED", "associationTypeId": 202}
          ]
      }
  ]

  if company_id:
      associations.append({
          "to": {"id": str(company_id)},
          "types": [
              {"associationCategory": "HUBSPOT_DEFINED", "associationTypeId": 190}
          ]
      })

  payload = {
      "properties": {
          "hs_timestamp": formatted_timestamp,
          "hs_note_body": str(note)
      },
      "associations": associations
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
