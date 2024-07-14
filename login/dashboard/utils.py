import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build
from django.conf import settings

SCOPES = ['https://www.googleapis.com/auth/calendar']

def create_calendar_event(doctor, appointment):
    credentials = service_account.Credentials.from_service_account_file(
        settings.GOOGLE_CREDENTIALS_FILE, scopes=SCOPES)
    service = build('calendar', 'v3', credentials=credentials)

    event = {
        'summary': 'Appointment with {}'.format(appointment.patient.username),
        'description': 'Appointment details',
        'start': {
            'dateTime': appointment.start_time.isoformat(),
            'timeZone': 'UTC',
        },
        'end': {
            'dateTime': (appointment.start_time + datetime.timedelta(minutes=45)).isoformat(),
            'timeZone': 'UTC',
        },
        'attendees': [
            {'email': doctor.email},
            {'email': appointment.patient.email},
        ],
    }

    event = service.events().insert(calendarId='primary', body=event).execute()
    print('Event created: %s' % (event.get('htmlLink')))