import os
import json
from datetime import datetime

from custom_decorators import handle_http_error
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from binancewallet import get_account_balances

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

# The ID and range of a sample spreadsheet.
SPREADSHEET_ID = os.getenv('SHEET')
CREDENTIALS = json.loads(os.getenv('CREDENTIALS'))
TOKEN = json.loads(os.getenv('TOKEN'))

def get_balance():
  coins_values = get_account_balances()
  values = [[]]
  today = datetime.now().strftime('%d-%m-%Y %H:%M:%S')
  values[0].append(today)
  
  for coin, value in coins_values:
      values[0].append(round(value,2))
  print(values)
  return values

@handle_http_error
def nearest_empty_cell(creds,column='A'):
  range = f'{column}1:{column}1000'
  service = build("sheets", "v4", credentials=creds)

  result = (
      service.spreadsheets()
      .values()
      .get(spreadsheetId=SPREADSHEET_ID, range=range)
      .execute()
  )
  index = len(result.get("values", [])) + 1
  return f'{column}{index}'

def get_right_creds():
  creds = None

  if TOKEN:
    creds = Credentials.from_authorized_user_info(TOKEN, SCOPES)
  # If there are no (valid) credentials available, let the user log in.

  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_config(
          CREDENTIALS, SCOPES
      )
      creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    os.environ['TOKEN'] = creds.to_json()
  return creds

@handle_http_error
def update_transactions(creds):
  range = nearest_empty_cell(creds)
  print('started to update')
  service = build("sheets", "v4", credentials=creds)
  service.spreadsheets().values().update(
      spreadsheetId=SPREADSHEET_ID,
      range=range,
      valueInputOption="USER_ENTERED",
      body={"values": get_balance()}
  ).execute()

def main():
  credentials = get_right_creds()
  update_transactions(credentials)



if __name__ == "__main__":
  main()
