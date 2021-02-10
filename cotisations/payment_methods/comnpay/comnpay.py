"""cotisations.payment_utils.comnpay
The module in charge of handling the negociation with Comnpay
for online payment
"""

import base64
import hashlib
import time
from collections import OrderedDict
from random import randrange


class Transaction:
    """The class representing a transaction with all the functions
    used during the negociation
    """

    def __init__(
        self,
        vad_number="",
        secret_key="",
        urlRetourOK="",
        urlRetourNOK="",
        urlIPN="",
        source="",
        typeTr="D",
    ):
        self.vad_number = vad_number
        self.secret_key = secret_key
        self.urlRetourOK = urlRetourOK
        self.urlRetourNOK = urlRetourNOK
        self.urlIPN = urlIPN
        self.source = source
        self.typeTr = typeTr
        self.idTransaction = ""

    def buildSecretHTML(self, produit="Produit", montant="0.00", idTransaction=""):
        """Build an HTML hidden form with the different parameters for the
        transaction
        """
        if idTransaction == "":
            self.idTransaction = str(time.time())
            self.idTransaction += self.vad_number
            self.idTransaction += str(randrange(999))
        else:
            self.idTransaction = idTransaction

        array_tpe = OrderedDict(
            montant=str(montant),
            idTPE=self.vad_number,
            idTransaction=self.idTransaction,
            devise="EUR",
            lang="fr",
            nom_produit=produit,
            source=self.source,
            urlRetourOK=self.urlRetourOK,
            urlRetourNOK=self.urlRetourNOK,
            typeTr=str(self.typeTr),
        )

        if self.urlIPN != "":
            array_tpe["urlIPN"] = self.urlIPN

        array_tpe["key"] = self.secret_key
        strWithKey = base64.b64encode(bytes("|".join(array_tpe.values()), "utf-8"))
        del array_tpe["key"]
        array_tpe["sec"] = hashlib.sha512(strWithKey).hexdigest()

        ret = ""
        for key in array_tpe:
            ret += '<input type="hidden" name="{k}" value="{v}"/>'.format(
                k=key, v=array_tpe[key]
            )

        return ret

    @staticmethod
    def validSec(values, secret_key):
        """ Check if the secret value is correct """
        if "sec" in values:
            sec = values["sec"]
            del values["sec"]
            strWithKey = hashlib.sha512(
                base64.b64encode(
                    bytes("|".join(values.values()) + "|" + secret_key, "utf-8")
                )
            ).hexdigest()
            return strWithKey.upper() == sec.upper()
        else:
            return False
