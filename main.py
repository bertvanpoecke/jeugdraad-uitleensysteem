import os
import classDefinitions

from sheetFunctions import getRequests
from calenderFunctions import addRequest
from mailFunctions import makeDraftMails
from invoiceFunctions import createInvoice

# ------------------------------------

def main():
    requests = getRequests()

    for request in requests:
        addRequest( request )
        invoicePath = ""
        if request.mNotaID:
            invoicePath = createInvoice( request )
        if request.mSendMails:
            makeDraftMails( request, invoicePath )

    if not requests:
        print("No requests to handle")



if __name__ == '__main__':
    main()
