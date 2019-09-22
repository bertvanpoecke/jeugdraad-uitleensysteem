import json
import os

settingsPath = "./settings.json"
settings = {}

# #############

def GetApplicationName():
    LoadSettings()
    assert settings, "Settings are not loaded yet!"
    return settings[ "applicationname" ]

def GetClientSecret():
    LoadSettings()
    assert settings, "Settings are not loaded yet!"
    return settings[ "clientsecret" ]

def GetCalendarSettings():
    LoadSettings()
    assert settings, "Settings are not loaded yet!"
    return settings[ "calendar" ]

def GetDriveSettings():
    LoadSettings()
    assert settings, "Settings are not loaded yet!"
    return settings[ "drive" ]

def GetInvoiceSettings():
    LoadSettings()
    assert settings, "Settings are not loaded yet!"
    return settings[ "invoice" ]

def GetMailSettings():
    LoadSettings()
    assert settings, "Settings are not loaded yet!"
    return settings[ "mail" ]

def GetSheetSettings():
    LoadSettings()
    assert settings, "Settings are not loaded yet!"
    return settings[ "sheet" ]

# #############

def DumpJSON( inDictionary ):
    print( json.dumps( inDictionary, indent=4, separators=(", ", " : ") ) )

def ReadSettings( inPath ):
    try:
        with open( inPath ) as file:
            return json.load( file )
    except:
        print( "Settings json file cannot be opened or has invalid format." )
        exit()

def LoadSettings():
    global settings    # Needed to modify global copy of "settings"
    settings = ReadSettings( inPath=settingsPath )
    return settings

# #############

def TestReadSettings():
    LoadSettings()
    DumpJSON(GetApplicationName())
    DumpJSON(GetClientSecret())
    DumpJSON(GetCalendarSettings())
    DumpJSON(GetDriveSettings())
    DumpJSON(GetInvoiceSettings())
    DumpJSON(GetMailSettings())
    DumpJSON(GetSheetSettings())

# if __name__ == "__main__":
#     TestReadSettings()