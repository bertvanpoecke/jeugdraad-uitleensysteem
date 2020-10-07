from __future__ import print_function
import httplib2
import os

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

from enum import Enum
from classDefinitions import Material, Request
from datetime import datetime, timedelta
from settings import GetApplicationName, GetClientSecret, GetSheetSettings

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# ---------------------------------------
class ColumnTitles( Enum ):
    kAanvraagDatum = 0
    kVoornaamAanvrager = 1
    kNaamAanvrager = 2
    kVereniging = 3
    kGsm = 4
    kEmail = 5
    kVan = 6
    kTot = 7
    kDatumEvenement = 8
    kTitelEvenement = 9
    kOpmerking = 10
    kNotaID = 11
    kWaarborg = 12
    kProcessRequest = 13
    kSendMails = 14
    kBeamer1 = 15
    kBeamer2 = 16
    kVGA = 17
    kProjectiescherm = 18
    kGeluidsinstallatie = 19
    k800watt = 20
    kGeluidsmeter = 21
    kRookmachine = 22
# ---------------------------------------


# ---------------------------------------

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/sheets.googleapis.com-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/spreadsheets.readonly'
CLIENT_SECRET_FILE = GetClientSecret()
APPLICATION_NAME = GetApplicationName()

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
                                   'sheets.googleapis.com-python-quickstart.json')

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

def getData():
    """Shows basic usage of the Sheets API.

    Creates a Sheets API service object and prints the names and majors of
    students in a sample spreadsheet:
    https://docs.google.com/spreadsheets/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms/edit
    """
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?'
                    'version=v4')
    service = discovery.build('sheets', 'v4', http=http,
                              discoveryServiceUrl=discoveryUrl)

    spreadsheetId = GetSheetSettings()[ "spreadsheetId" ]

    rangeName = 'Aanvragen!A3:X'
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheetId, range=rangeName).execute()
    values = result.get('values', [])

    return values

def getRequests():
    values = getData()
    requests = []
    if not values:
        print('No data found.')
    else:
        for row in values:
            if row[ ColumnTitles.kProcessRequest.value ] == "x":
                try:
                    fromDate = datetime.strptime( row[ ColumnTitles.kVan.value ], '%d/%m/%Y' )
                except:
                    # fromDate = datetime.strptime( row[ ColumnTitles.kVan.value ], '%d-%m-%Y' )
                    fromDate = datetime.strptime( row[ ColumnTitles.kVan.value ], '%Y-%m-%d' )
                try:
                    toDate = datetime.strptime( row[ ColumnTitles.kTot.value ], '%d/%m/%Y' ) + timedelta( days=1 )
                except:
                    # toDate = datetime.strptime( row[ ColumnTitles.kTot.value ], '%d-%m-%Y' ) + timedelta( days=1 )
                    toDate = datetime.strptime( row[ ColumnTitles.kTot.value ], '%Y-%m-%d' ) + timedelta( days=1 )
                try:
                    eventDate = datetime.strptime( row[ ColumnTitles.kDatumEvenement.value ], '%d/%m/%Y' )
                except:
                    # eventDate = datetime.strptime( row[ ColumnTitles.kDatumEvenement.value ], '%d-%m-%Y' )
                    eventDate = datetime.strptime( row[ ColumnTitles.kDatumEvenement.value ], '%Y-%m-%d' )

                request = Request(
                    row[ ColumnTitles.kVoornaamAanvrager.value ],
                    row[ ColumnTitles.kNaamAanvrager.value ],
                    row[ ColumnTitles.kVereniging.value ],
                    row[ ColumnTitles.kGsm.value ],
                    row[ ColumnTitles.kEmail.value ],
                    fromDate,
                    toDate,
                    eventDate,
                    row[ ColumnTitles.kTitelEvenement.value ],
                    row[ ColumnTitles.kNotaID.value ],
                    row[ ColumnTitles.kSendMails.value ] == "x"
                )
                try:
                    if row[ ColumnTitles.kBeamer1.value ] != "":
                        request.addMaterial( Material.kBeamer1 )
                except:
                    pass
                try:
                    if row[ ColumnTitles.kBeamer2.value ] != "":
                        request.addMaterial( Material.kBeamer2 )
                except:
                    pass
                try:
                    if row[ ColumnTitles.kVGA.value ] != "":
                        request.addMaterial( Material.kVGA )
                except:
                    pass
                try:
                    if row[ ColumnTitles.kProjectiescherm.value ] != "":
                        request.addMaterial( Material.kProjectiescherm )
                except:
                    pass
                try:
                    if row[ ColumnTitles.kGeluidsinstallatie.value ] != "":
                        request.addMaterial( Material.kGeluidsinstallatie )
                except:
                    pass
                try:
                    if row[ ColumnTitles.k800watt.value ] != "":
                        request.addMaterial( Material.k800watt )
                except:
                    pass
                try:
                    if row[ ColumnTitles.kGeluidsmeter.value ] != "":
                        request.addMaterial( Material.kGeluidsmeter )
                except:
                    pass
                try:
                    if row[ ColumnTitles.kRookmachine.value ] != "":
                        request.addMaterial( Material.kRookmachine )
                except:
                    pass

                requests.append( request )

                # datetime_object = datetime.strptime(request.mDatumEvenement, '%d/%m/%Y')
                # print(request.mVoornaamAanvrager)
                # print(request.mDatumEvenement)
                # print(request.mMateriaalLijst)
                # print(datetime_object.day)
                # print(datetime_object.month)
                # print(datetime_object.year)


    return requests

