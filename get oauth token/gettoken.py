import os
import json
import pickle
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials

# SCOPES = ['https://www.googleapis.com/auth/calendar']
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

name = 'gmail'

def main():
    creds = None
    if os.path.exists('token.json'):
        with open('token.json', 'r') as token:
            creds = Credentials.from_authorized_user_info(json.load(token), SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                f'{name} oauth.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open(f'{name} token.json', 'w') as token:
            token.write(creds.to_json())

    print("Refresh Token:", creds.refresh_token)

if __name__ == '__main__':
    main()
