from __future__ import print_function
import httplib2
import os
import io

from apiclient import discovery
from apiclient.http import MediaIoBaseDownload

from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

from classDefinitions import Request
from settings import GetApplicationName, GetClientSecret, GetDriveSettings

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None


jeugdraadDrivePath = GetDriveSettings()[ "localJeugdraadDrivePath" ]

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/drive-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/drive'
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
                                   'drive-python-quickstart.json')

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

def downloadInvoice( inRequest ):
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('drive', 'v3', http=http)

    invoiceTemplateId = GetDriveSettings()[ "invoiceTemplateId" ]
    filePath = jeugdraadDrivePath + str( inRequest.mNotaID ) + "_onkostennota_" + inRequest.mVereniging + ".pdf"

    if os.path.isfile( filePath ):
        try:
            print( "### Invoice already exists. Invoice redownloaded." )
            os.remove( filePath )
        except OSError:
            print( "### Invoice already exists. Could not remove file." )
            exit
            pass

    io.FileIO( filePath, 'wb').write( service.files().export_media( fileId=invoiceTemplateId, mimeType='application/pdf' ).execute() )
    # print( filePath )
    return filePath