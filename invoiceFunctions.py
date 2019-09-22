from __future__ import print_function
import httplib2
import os

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

from classDefinitions import Request, Material
from driveFunctions import downloadInvoice
from settings import GetApplicationName, GetClientSecret, GetInvoiceSettings

from pprint import pprint

from googleapiclient import discovery

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/sheets.googleapis.com-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/spreadsheets'
CLIENT_SECRET_FILE = GetClientSecret()
APPLICATION_NAME = GetApplicationName()

kTableRange = "A17:C33"

def GetWaarborgData( inMaterialList ):
    waarborgValues = {
        Material.kBeamer1: 100,
        Material.kBeamer2: 100,
        Material.kVGA: 50,
        Material.kProjectiescherm: 250,
        Material.kGeluidsinstallatie: 250,
        Material.k800watt: 100,
        Material.kGeluidsmeter: 250,
        Material.kRookmachine: 50
    }

    waarborg = 0
    for material in inMaterialList:
        waarborg = waarborg + waarborgValues.get( material, 0 )

    return [ "Waarborg", 1, min( 250, waarborg ) ]

def GetMaterialData( inMaterial ):
    switcher = {
        Material.kBeamer1: [ "Ontlening beamer 1", 1, 25 ],
        Material.kBeamer2: [ "Ontlening beamer 2", 1, 25 ],
        Material.kVGA: [ "Lange VGA-kabel", 1, 0 ],
        Material.kProjectiescherm: [ "Ontlening groot projectiescherm", 1, 50 ],
        Material.kGeluidsinstallatie: [ "Ontlening geluidsinstallatie", 1, 100 ],
        Material.k800watt: [ "Ontlening 800 Watt set + micro's", 1, 75 ],
        Material.kGeluidsmeter: [ "Ontlening geluidsmeter", 1, 0 ],
        Material.kRookmachine: [ "Ontlening rookmachine", 1, 15 ],
    }
    return switcher.get( inMaterial, [] )


def GetTableData( inMaterialList ):
    tableData = []

    for material in inMaterialList:
        tableData.append( GetMaterialData( material ) )
    tableData.append( GetWaarborgData( inMaterialList ) )

    return tableData


def GetData( inRequest ):
    idData = [ [ inRequest.mNotaID ] ]
    requesterData = [
        [ inRequest.mVoornaamAanvrager ],
        [ inRequest.mNaamAanvrager ],
        [ inRequest.mVereniging ],
        [],
        [ inRequest.mGsm ],
        [ inRequest.mEmail ]
    ]
    tableData = GetTableData( inRequest.mMateriaalLijst )

    data = [
        {
            'range': "D3",
            'values': idData
        },
        {
            'range': "D6:D11",
            'values': requesterData
        },
        {
            'range': "A17:C33",
            'values': tableData
        }
    ]

    return data

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
                                   'sheets.googleapis.com-python-quickstart-invoice.json')

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

def createInvoice( inRequest ):
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

    spreadsheetId = GetInvoiceSettings()[ "spreadsheetId" ]

    # body_clear = {
    #     "spreadsheetId": spreadsheetId,
    #     "clearedRange": kTableRange,
    # }
    result_clear = service.spreadsheets().values().clear(spreadsheetId=spreadsheetId, range=kTableRange, body={}).execute()

    body = {
        'valueInputOption': 'USER_ENTERED',
        'data': GetData( inRequest )
    }
    result = service.spreadsheets().values().batchUpdate(
        spreadsheetId=spreadsheetId, body=body).execute()

    return downloadInvoice( inRequest )








