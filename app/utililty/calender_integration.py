from __future__ import print_function
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
import datetime
import google_auth_oauthlib.flow
from app import app
import flask
import json
import os


# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar']


@app.route('/api/start_registration', methods=['GET'])
def start_registration():
    if not getattr(app, 'credentials', None):
        flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file('credentials.json', SCOPES)
        flow.redirect_uri = os.environ.get('redirect_uris')
        # Generate URL for request to Google's OAuth 2.0 server.
        # Use kwargs to set optional request parameters.
        authorization_url, state = flow.authorization_url(
            # Enable offline access so that you can refresh an access token without
            # re-prompting the user for permission. Recommended for web server apps.
            access_type='offline',
            # Enable incremental authorization. Recommended as a best practice.
            include_granted_scopes='true')
        print(authorization_url)
        with app.app_context():
            app.state = state
    return flask.Response(response=json.dumps({"message": "Added Successfully"}),
                          status=200, content_type="application/json")


@app.route('/api/register_credentials', methods=['GET'])
def register_credentials():
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        'credentials.json',
        scopes=SCOPES,
        state=flask.request.args['state'])
    flow.redirect_uri = os.environ.get('redirect_uris')

    authorization_response = flask.request.url
    print(authorization_response)
    flow.fetch_token(authorization_response=authorization_response)

    # Store the credentials in the session.
    # ACTION ITEM for developers:
    #     Store user's access and refresh tokens in your data store if
    #     incorporating this code into your real app.
    with app.app_context():
        app.credentials = flow.credentials
        print(dir(flow.credentials))
    return flask.Response(response=json.dumps({"message": "Added Successfully"}),
                          status=200, content_type="application/json")


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
    mail_body['reminders'] = {'useDefault': False, 'overrides': [{'method': 'email', 'minutes': 60},
                                                                 {'method': 'popup', 'minutes': 10}]}
    if getattr(app, 'credentials', None):
        service = build('calendar', 'v3', credentials=app.credentials)

        event = service.events().insert(calendarId='primary', body=mail_body).execute()
        print(event)
    else:
        raise Exception('Created entry in calender but failed to call google as Calender session has expired')
