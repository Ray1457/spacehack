from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import os.path
import json
from email.mime.text import MIMEText
import base64

# If modifying these SCOPES, delete the file token.json.
SCOPES_CALENDER = ['https://www.googleapis.com/auth/calendar']

TOKEN_FILE_CALENDER = 'calender token.json'

def calendar_auth():
    creds = None
    if os.path.exists(TOKEN_FILE_CALENDER) :
        with open(TOKEN_FILE_CALENDER, 'r') as token:
            creds = Credentials.from_authorized_user_info(json.load(token), SCOPES_CALENDER)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            print("Invalid or missing credentials")
    
    service = build('calendar', 'v3', credentials=creds)
    return service

import uuid

def create_meeting(summary, start_time, end_time):
    service = calendar_auth()
    
    event = {
        'summary': summary,
        'start': {
            'dateTime': start_time,
            'timeZone': 'Asia/Kolkata',
        },
        'end': {
            'dateTime': end_time,
            'timeZone': 'Asia/Kolkata',
        },
        'conferenceData': {
            'createRequest': {
                'requestId': str(uuid.uuid4()),
                'conferenceSolutionKey': {
                    'type': 'hangoutsMeet'
                }
            }
        }
    }
    
    try:
        event = service.events().insert(
            calendarId='primary',
            body=event,
            conferenceDataVersion=1
        ).execute()

        return event.get('hangoutLink')
    
    except Exception as error:
        print(f'An error occurred: {error}')
        if hasattr(error, 'content'):
            print(error.content)
        return None

# print(create_meeting('Yoga', '2024-08-18T17:30:00' ,'2024-08-18T18:00:00'))






SCOPES = ['https://www.googleapis.com/auth/gmail.send']
TOKEN_FILE = 'gmail token.json'

def gmail_auth():
    creds = None
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'r') as token:
            creds = Credentials.from_authorized_user_info(json.load(token), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            print("Invalid or missing credentials")

    service = build('gmail', 'v1', credentials=creds)
    return service

def send_email(to,sub,body):
    service  = gmail_auth()
    message = MIMEText(body)
    message['to'] = to
    message['from'] = 'noreply.spaceit@gmail.com'
    message['subject'] = sub
    message = {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}
    try:
        message = service.users().messages().send(userId='me', body=message).execute()
        print('Message Id: %s' % message['id'])
        return message
    except Exception as error:
        print(f'An error occurred: {error}')
        return None