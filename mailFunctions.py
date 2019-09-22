from __future__ import print_function
import httplib2
import os

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

from classDefinitions import Request, Material
from settings import GetApplicationName, GetClientSecret, GetMailSettings

import base64
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import mimetypes

from apiclient import errors


try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/gmail-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/gmail.compose'
CLIENT_SECRET_FILE = GetClientSecret()
APPLICATION_NAME = GetApplicationName()

kJeugdraadGmail = GetMailSettings()[ "JeugdraadGmail" ]
kMailJeugddienst = GetMailSettings()[ "MailJeugddienst" ]
kMailVrijetijdsdienst = GetMailSettings()[ "MailVrijetijdsdienst" ]
kMailFinancieelVerantwoordelijke = GetMailSettings()[ "MailFinancieelVerantwoordelijke" ]
kSubjectConfirmation = "[Jeugdraad: Uitleendienst] Bevestiging aanvraag materiaal: "
kUserAgreementPath = GetMailSettings()[ "UserAgreementPath" ]
kUserAgreementLink = GetMailSettings()[ "UserAgreementLink" ]

def MaterialListToString( inMaterialList ):
    string = ""
    for material in inMaterialList:
        string = string + "<li>" + material.value + "</li>"
    return "<ul>" + string + "</ul>"

def GetConfirmationMailBody( inRequest ):
    return """
    <html>
        <head></head>
        <body>
            <p>
                Dag {name}
            </p>
            <p>
                Jullie reservering van het materiaal is goedgekeurd voor de aangevraagde termijn ({van} - {tot}). Deze kan u ook terugvinden op de <a href="https://www.jeugdwichelen.be/uitleendienst/uitleenkalender/">uitleenkalender</a>.
            </p>
            <p>
                <strong>Ontlening</strong><br>
                Inhoud van jullie ontlening:
                {materialList}
            </p>
            <p>
                Alle gebruikershandleidingen van het ontleende materiaal zijn beschikbaar op <a href="https://www.jeugdwichelen.be/uitleendienst/materiaal/">onze site</a>.
            </p>
            <p>
                Wij raden jullie ten sterkste aan om het ontleende materiaal te controleren voor gebruik. Beschadigingen, ontbrekend materiaal e.d. moeten onmiddellijk gemeld worden aan de uitleendienst. Indien dit pas gebeurt bij het terugbrengen van het materiaal (na gebruik) zullen de kosten aan u aangerekend worden.
                Voor verdere details en info verwijzen wij u door naar het <a href={reglementLink}>uitleenreglement</a>.
            </p>
            <p>
                <strong>Afhalen/terugbrengen</strong><br>
                Afhalen en terugbrengen van het materiaal kan elke werkdag aan de balie van David Levantaci, jeugdconsulent van de gemeente Wichelen.
                Bij het afhalen en terug brengen van het materiaal dient te worden rekening gehouden met de openingsuren van het Sociaal Huis, Oud dorp 2 te Wichelen. Deze kan u <a href="http://www.jeugdwichelen.be/contact/">hier</a> terugvinden.
            </p>
            <p>
                Vragen of opmerking kan u richten naar het algemeen e-mailadres van de Wichelse Jeugdraad: jeugdwichelen@gmail.com. Wij helpen u graag verder.
            </p>
            <p>
                Bijlage:<br>
                <ul>
                    <li><a href={reglementLink}>uitleenreglement en gebruiksvoorwaarden (pdf)</a></li>
                </ul>
            </p>
            <p>
                Veel plezier met jullie activiteit!<br>
                Met vriendelijke groeten
            </p>
            <p>
                <div style="color:#7F7F7F; font-weight:bold;">Bert Van Poecke</div>
                Bestuurslid Jeugdraad Wichelen<br>
                Verantwoordelijke Uitleendienst Jeugdraad
            </p>
            <p>
                jeugdwichelen@gmail.com
            </p>
        </body>
    </html>
    """.format(name=inRequest.mVoornaamAanvrager, van=inRequest.mVan.date().strftime("%d/%m/%Y"), tot=inRequest.mTot.date().strftime("%d/%m/%Y"), materialList=MaterialListToString( inRequest.mMateriaalLijst ), reglementLink=kUserAgreementLink )

def GetConfirmationMailBodyWithInvoice( inRequest, inInvoicePath ):
    return """
    <html>
        <head></head>
        <body>
            <p>
                Beste {name}
            </p>
            <p>
                Uw aanvraag van het materiaal is goedgekeurd voor de aangegeven termijn ({van} - {tot}). Deze kan u ook terugvinden op de <a href="https://www.jeugdwichelen.be/uitleendienst/uitleenkalender/">uitleenkalender</a>.<br>
                U vindt de onkostennota voor uw aangevraagde materiaal als bijlage.
                Alle betalingsgegevens staan hierin vermeld.
            </p>
            <p>
                Het bedrag dient u tegen de ontlening overgeschreven te hebben volgens de instructies op de onkostennota.
                Indien de waarborg niet binnen de voorziene tijd kan gestort worden, dient deze cash te worden betaald bij afhaling.
                Na nazicht van het materiaal zal de waarborg binnen de 10 werkdagen worden teruggestort op uw rekening.
            </p>
            <p>
                <strong>Ontlening</strong><br>
                Inhoud van jullie ontlening:
                {materialList}
            </p>
            <p>
                Alle gebruikershandleidingen van het ontleende materiaal zijn beschikbaar op <a href="https://www.jeugdwichelen.be/uitleendienst/materiaal/">onze site</a>.
            </p>
            <p>
                Wij raden jullie ten sterkste aan om het ontleende materiaal te controleren voor gebruik. Beschadigingen, ontbrekend materiaal e.d. moeten onmiddellijk gemeld worden aan de uitleendienst. Indien dit pas gebeurt bij het terugbrengen van het materiaal (na gebruik) zullen de kosten aan u aangerekend worden.
                Voor verdere details en info verwijzen wij u door naar het uitleenreglement (zie bijlage).
            </p>
            <p>
                <strong>Afhalen/terugbrengen</strong><br>
                Afhalen en terugbrengen van het materiaal kan elke werkdag aan de balie van David Levantaci, jeugdconsulent van de gemeente Wichelen.
                Bij het afhalen en terug brengen van het materiaal dient te worden rekening gehouden met de openingsuren van het Sociaal Huis, Oud dorp 2 te Wichelen. Deze kan u <a href="http://www.jeugdwichelen.be/contact/">hier</a> terugvinden.
            </p>
            <p>
                Vragen of opmerking kan u richten naar het algemeen e-mailadres van de Wichelse Jeugdraad: jeugdwichelen@gmail.com. Wij helpen u graag verder.
            </p>
            <p>
                Bijlage:<br>
                <ul>
                    <li><a href={reglementLink}>uitleenreglement en gebruiksvoorwaarden (pdf)</a></li>
                    <li>onkostennota (pdf): {onkostennota}</li>
                </ul>
            </p>
            <p>
                Met vriendelijke groeten
            </p>
            <p>
                <div style="color:#7F7F7F; font-weight:bold;">Bert Van Poecke</div>
                Bestuurslid Jeugdraad Wichelen<br>
                Verantwoordelijke Uitleendienst Jeugdraad
            </p>
            <p>
                jeugdwichelen@gmail.com
            </p>
        </body>
    </html>
    """.format(name=inRequest.mVoornaamAanvrager, van=inRequest.mVan.date().strftime("%d/%m/%Y"), tot=inRequest.mTot.date().strftime("%d/%m/%Y"), materialList=MaterialListToString( inRequest.mMateriaalLijst ), onkostennota=os.path.basename( inInvoicePath ), reglementLink=kUserAgreementLink )


def create_message_with_attachment( sender, to, subject, html_message_text, files, inContactFinancial ):
    """Create a message for an email.

    Args:
    sender: Email address of the sender.
    to: Email address of the receiver.
    subject: The subject of the email message.
    message_text: The text of the email message.
    file: The path to the file to be attached.

    Returns:
    An object containing a base64url encoded email object.
    """
    message = MIMEMultipart()
    message['To'] = to
    if inContactFinancial:
        message['Cc'] = sender + ", " + kMailJeugddienst + ", " + kMailVrijetijdsdienst + ", " + kMailFinancieelVerantwoordelijke
    else:
        message['Cc'] = sender + ", " + kMailJeugddienst + ", " + kMailVrijetijdsdienst
    message['From'] = sender
    message['Subject'] = subject

    msg = MIMEText( html_message_text, 'html' )
    message.attach(msg)

    if files:
        # for file in files:
        file = files[ 0 ]
        content_type, encoding = mimetypes.guess_type( file )

        if content_type is None or encoding is not None:
            content_type = 'application/octet-stream'

        main_type, sub_type = content_type.split('/', 1)

        # print( main_type, sub_type)

        fp = open(file, 'rb')
        msg = MIMEBase(main_type, sub_type)
        msg.set_payload(fp.read())
        fp.close()

        encoders.encode_base64(msg)

        filename = os.path.basename(file)
        msg.add_header('Content-Disposition', 'attachment', filename=filename)
        message.attach(msg)

    return {'raw': base64.urlsafe_b64encode(message.as_string())}


def create_draft(service, user_id, message_body):
    """Create and insert a draft email. Print the returned draft's message and id.

    Args:
    service: Authorized Gmail API service instance.
    user_id: User's email address. The special value "me"
    can be used to indicate the authenticated user.
    message_body: The body of the email message, including headers.

    Returns:
    Draft object, including draft id and message meta data.
    """
    try:
        message = {'message': message_body}
        draft = service.users().drafts().create(userId=user_id, body=message).execute()

        print('Draft created. Draft id: %s' % (draft['id']) )

        return draft
    except errors.HttpError, error:
        print( 'An error occurred: %s' % error )
        return None


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
                                   'gmail-python-quickstart.json')

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

def makeDraftMails( inRequest, inInvoicePath ):
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('gmail', 'v1', http=http)

    if inInvoicePath:
        htmlMessageText = GetConfirmationMailBodyWithInvoice( inRequest, inInvoicePath )
        # files = [ kUserAgreementPath, inInvoicePath ]
        files = [ inInvoicePath ]
        contactFinancial = True
    else:
        htmlMessageText = GetConfirmationMailBody( inRequest )
        # files = [ kUserAgreementPath ]
        files = []
        contactFinancial = False

    message = create_message_with_attachment( kJeugdraadGmail, inRequest.mEmail, kSubjectConfirmation + inRequest.mVereniging, htmlMessageText, files, contactFinancial )
    draft = create_draft( service, 'me', message )
