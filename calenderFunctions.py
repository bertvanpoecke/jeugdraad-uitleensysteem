from __future__ import print_function
import httplib2
import os

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

from classDefinitions import Request, Material
from settings import GetApplicationName, GetClientSecret, GetCalendarSettings

import datetime
import pytz

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/calendar-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/calendar'
CLIENT_SECRET_FILE = GetClientSecret()
APPLICATION_NAME = GetApplicationName()

def ToCalendarID( inCalendar ):
    calendarSettings = GetCalendarSettings()
    switcher = {
        Material.kBeamer1: calendarSettings[ "Beamer1" ],
        Material.kBeamer2: calendarSettings[ "Beamer2" ],
        Material.kVGA: calendarSettings[ "VGA" ],
        Material.kProjectiescherm: calendarSettings[ "Projectiescherm" ],
        Material.kGeluidsinstallatie: calendarSettings[ "Geluidsinstallatie" ],
        Material.k800watt: calendarSettings[ "800watt" ],
        Material.kGeluidsmeter: calendarSettings[ "Geluidsmeter" ],
        Material.kRookmachine: calendarSettings[ "Rookmachine" ]
    }
    return switcher.get( inCalendar, "" )

def DoesOverlap( inService, inRequest ):
    calendarsToCheck = []
    for material in inRequest.mMateriaalLijst:
        calendarId = ToCalendarID( material )
        if not calendarId:
            print( "Calendar ID not found" )
            return True
        calendarsToCheck.append( { 'id': calendarId } )

    tz = pytz.timezone('Europe/Brussels')
    timeMin = tz.localize(inRequest.mVan).isoformat()
    timeMax = tz.localize(inRequest.mTot).isoformat()
    print(timeMin)
    print(timeMax)
    body = {
        "timeMin": timeMin,
        "timeMax": timeMax,
        "timeZone": 'Europe/Brussels',
        "items": calendarsToCheck
    }

    eventsResult = inService.freebusy().query( body=body ).execute()
    cal_dict = eventsResult[ u'calendars' ]
    for cal_name in cal_dict:
        if not not cal_dict[cal_name][u'busy']:
            print( "One or more calendars are already busy" )
            return True
    return False

def GetEvents( inRequest ):
    events = []

    for material in inRequest.mMateriaalLijst:
        calendarID = ToCalendarID( material )
        if not calendarID:
            print( "Calendar ID not found" )
            continue

        event = {
            'summary': inRequest.mVereniging + " - " + material.value,
            'description': material.value,
            'start': {
                'date': inRequest.mVan.date().isoformat(),
                'timeZone': 'Europe/Brussels',
            },
            'end': {
                'date': inRequest.mTot.date().isoformat(),
                'timeZone': 'Europe/Brussels',
            },
        }
        print( event )
        events.append( {'calendarID': calendarID, 'event': event} )

    return events

def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'calendar-python-quickstart.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

def addRequest( inRequest ):
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)

    if DoesOverlap( service, inRequest ):
        print( "### Event overlap! ### \t Please check calendar at dates: " + inRequest.mVan.date().isoformat() + " >> " + inRequest.mTot.date().isoformat() )

    events = GetEvents( inRequest )
    if not events:
        print( "No events to process" )
    for event in events:
        result = service.events().insert( calendarId=event[ "calendarID" ], body=event[ "event" ] ).execute()
        print( 'Event created: %s, %s' % ( event[ "event" ][ "summary" ], result.get( 'htmlLink' ) ) )

