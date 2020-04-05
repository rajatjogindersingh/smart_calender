from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import datetime

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar']


def main(event: dict):
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)

    event = service.events().insert(calendarId='primary', body=event).execute()
    print('Event created: %s' % (event.get('htmlLink')))


def send_mail(booking_slot: object, booking_date: object, user_objects: list):
    mail_body = dict()
    mail_body['summary'] = booking_slot.summary
    mail_body['description'] = booking_slot.description
    start_time = datetime.datetime(year=booking_date.year, month=booking_date.month, day=booking_date.day,
                                   hour=booking_slot.start_time.hour, minute=booking_slot.start_time.minute)
    end_time = datetime.datetime(year=booking_date.year, month=booking_date.month, day=booking_date.day,
                                 hour=booking_slot.end_time.hour, minute=booking_slot.end_time.minute)
    mail_body['start'] = {'dateTime': start_time.isoformat()+"+05:30"}
    mail_body['end'] = {'dateTime': end_time.isoformat()+"+05:30"}
    mail_body['attendees'] = [{'email': user_objects[0]}, {'email': user_objects[1]}]
    mail_body['sendUpdates'] = 'all'
    mail_body['reminders'] = {'useDefault': False, 'overrides': [{'method': 'email', 'minutes': 15},
                                                                 {'method': 'popup', 'minutes': 1}]}
    main(mail_body)
