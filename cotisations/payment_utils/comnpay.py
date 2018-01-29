import time
from random import randrange
import base64
import hashlib
from collections import OrderedDict
from itertools import chain

class Payment():

    vad_number = ""
    secret_key = ""
    urlRetourOK = ""
    urlRetourNOK = ""
    urlIPN = ""
    source = ""
    typeTr = "D"

    def __init__(self, vad_number = "", secret_key = "", urlRetourOK = "", urlRetourNOK = "", urlIPN = "", source="", typeTr="D"):
        self.vad_number = vad_number
        self.secret_key = secret_key
        self.urlRetourOK = urlRetourOK
        self.urlRetourNOK = urlRetourNOK
        self.urlIPN = urlIPN
        self.source = source
        self.typeTr = typeTr

    def buildSecretHTML(self, produit="Produit", montant="0.00", idTransaction=""):
        if idTransaction == "":
            self.idTransaction = str(time.time())+self.vad_number+str(randrange(999))
        else:
            self.idTransaction = idTransaction

        array_tpe   = OrderedDict(
                montant= str(montant),
                idTPE= self.vad_number,
                idTransaction= self.idTransaction,
                devise= "EUR",
                lang= 'fr',
                nom_produit= produit,
                source= self.source,
                urlRetourOK= self.urlRetourOK,
                urlRetourNOK= self.urlRetourNOK,
                typeTr= str(self.typeTr)
        )

        if self.urlIPN!="":
            array_tpe['urlIPN'] = self.urlIPN

        array_tpe['key'] = self.secret_key;
        strWithKey = base64.b64encode(bytes('|'.join(array_tpe.values()), 'utf-8'))
        del array_tpe["key"]
        array_tpe['sec'] = hashlib.sha512(strWithKey).hexdigest()

        ret = ""
        for key in array_tpe:
            ret += '<input type="hidden" name="'+key+'" value="'+array_tpe[key]+'"/>'

        return ret

    def validSec(self, values, secret_key):
        if "sec" in values:
            sec = values['sec']
            del values["sec"]
            strWithKey = hashlib.sha512(base64.b64encode(bytes('|'.join(values.values()) +"|"+secret_key, 'utf-8'))).hexdigest()
            return strWithKey.upper() == sec.upper()
        else:
            return False

