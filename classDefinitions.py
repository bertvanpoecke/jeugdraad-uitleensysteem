from enum import Enum

class Material( Enum ):
    kBeamer1 = "Beamer 1"
    kBeamer2 = "Beamer 2"
    kVGA = "Lange VGA kabel (25m)"
    kProjectiescherm = "Projectiescherm"
    kGeluidsinstallatie = "Geluidsinstallatie"
    k800watt = "800 Watt set"
    kGeluidsmeter = "Geluidsmeter"
    kRookmachine = "Rookmachine"

class Request:
    def __init__(self, inVoornaamAanvrager, inNaamAanvrager, inVereniging, inGsm, inEmail, inVan, inTot, inDatumEvenement, inTitelEvenement, inNotaID, inSendMails ):
        self.mVoornaamAanvrager = inVoornaamAanvrager
        self.mNaamAanvrager = inNaamAanvrager
        self.mVereniging = inVereniging
        self.mGsm = inGsm
        self.mEmail = inEmail
        self.mVan = inVan
        self.mTot = inTot
        self.mDatumEvenement = inDatumEvenement
        self.mTitelEvenement = inTitelEvenement
        self.mSendMails = inSendMails
        self.mNotaID = inNotaID
        self.mMateriaalLijst = []

    def addMaterial( self, inMateriaal ):
        self.mMateriaalLijst.append( inMateriaal )

