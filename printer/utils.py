# -*- coding: utf-8 -*-
import subprocess
import os

from django.template.loader import get_template
from django.core.mail import EmailMessage

from preferences.models import GeneralOption, AssoOption

from .models import Digicode

import datetime


def pdfinfo(file_path):
    """
    Uses pdfinfo to extract the PDF meta information.
    Returns metainfo in a dictionary.
    requires poppler-utils
    """
    def _extract(row):
        """Extracts the right hand value from a : delimited row"""
        row=row.decode()
        return row.split(':', 1)[1].strip()

    output = {}

    labels = ['Title', 'Author', 'Creator', 'Producer', 'CreationDate', 'ModDate',
              'Tagged', 'Pages', 'Encrypted', 'Page size',
              'File size', 'Optimized', 'PDF version']

    cmd_output = subprocess.check_output(['/usr/bin/pdfinfo', file_path])
    for line in cmd_output.splitlines():
        for label in labels:
            try:
                if label in line.decode():
                    output[label] = _extract(line)
            except UnicodeDecodeError:
                pass
    return output


def pdfbook(file_path):
    """
    Creates a booklet from a pdf
    requires texlive-extra-utils
    """
    _dir = os.path.dirname(file_path)
    _fname = os.path.basename(file_path)
    newfile = os.path.join(_dir, "pdfbook_%s" % (_fname,))
    check_output(
        ['/usr/bin/pdfbook',
         '--short-edge',
         file_path,
         '-o', newfile,
        ])
    return newfile

def send_mail_printer(client):
    """Sends an email to the client explaning how to get the printings"""

    template = get_template('printer/email_printer')
    code = Digicode._gen_code(client)

    printer_access_fr = "au quatrième (4) étage du bâtiment J (code B7806)"
    printer_access_en = "on fourth (4th) floor of building J (code B7806)"
    digicode = True

    end_validity = datetime.datetime.now() + datetime.timedelta(3)
    end_validity = str(end_validity.date())

    ctx = {
        'name': "{} {}".format(
            client.name,
            client.surname
        ),
        'printer_access_fr' : printer_access_fr,
        'printer_access_en' : printer_access_en,
        'digicode' : digicode,
        'code' : code,
        'end_validity' : end_validity,
        'contact_mail': AssoOption.get_cached_value('contact'),
        'asso_name': AssoOption.get_cached_value('name')
    }

    mail = EmailMessage(
        'Information',
        template.render(ctx),
        GeneralOption.get_cached_value('email_from'),
        [client.get_mail],
    )
    mail.send()
