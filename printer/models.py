# -*- mode: python; coding: utf-8 -*-

"""printer.models
Models of the printer application
Author : Maxime Bombar <bombar@crans.org>.
"""

from __future__ import unicode_literals

from numpy.random import randint
import unidecode

from django.core.files.storage import FileSystemStorage
from django.core.exceptions import ObjectDoesNotExist

from django.db import models
from django.forms import ValidationError
from django.utils.translation import ugettext_lazy as _
from django.template.defaultfilters import filesizeformat

from re2o.mixins import RevMixin, AclMixin
from re2o.field_permissions import FieldPermissionModelMixin
import users.models

from .validators import (
    FileValidator,
)

from .settings import (
        MAX_PRINTFILE_SIZE,
        ALLOWED_TYPES,
        PRICES,
        FORMAT_AVAILABLE,
        COLOR_CHOICES,
        DISPOSITIONS_AVAILABLE,
        STAPLING_OPTIONS,
        PERFORATION_OPTIONS,
)


import math

"""
- ```user_printing_path``` is a function that returns the path of the uploaded file, used with the FileField.
- ```Job``` is the main model of a printer job. His parent is the ```user``` model.
"""

def user_printing_path(instance, filename):
    """
    Defines the path where will be uploaded the files
    """
    # File will be uploaded to MEDIA_ROOT/printings/user_<id>/<filename>
    return 'printings/user_{0}/{1}'.format(instance.user.id, unidecode.unidecode(filename))


class Digicode(RevMixin, models.Model):
    """
    This is a model to represent a digicode, maybe should be an external app.
    """
    code = models.BigIntegerField(default=0, unique=True)
    user = models.ForeignKey('users.User', on_delete=models.PROTECT)
    created = models.DateTimeField(auto_now_add=True)
    used_time = models.DateTimeField(null=True)

    def _gen_code(user):
        try_again = True
        while try_again:
            try:
                code = randint(695895, 6958942)*1437+38
                Digicode.objects.get(code=code)
            except ObjectDoesNotExist:
                try_again = False
        digicode = Digicode.objects.create(code=code, user=user)
        digicode.save()
        return (str(code) + '#')

class PrintOperation(RevMixin, AclMixin, models.Model):
    """Abstract printing operation"""
    user = models.ForeignKey('users.User', on_delete=models.PROTECT)

    def can_edit(self, user_request, *args, **kwargs):
        if user_request.has_perm('printer.change_printoperation'):
            return True, None
        elif user_request == self.user:
            return True, None
        else:
            return False, _("This is not your print operation task")


class JobWithOptions(RevMixin, AclMixin, FieldPermissionModelMixin, models.Model):
    """
    This is the main model of printer application :

        - ```user``` is a ForeignKey to the User Application
        - ```file``` is the file to print
        - ```filename``` is the name of the file to print
        - ```starttime``` is the time when the job was launched
        - ```endtime``` is the time when the job was stopped.
            A job is stopped when it is either finished or cancelled.
        - ```status``` can be running, finished or cancelled.
        - ```club``` is blank in general. If the job was launched as a club then
            it is the id of the club.
        - ```price``` is the total price of this printing.

    Printing Options :

        - ```format``` is the paper format. Example: A4.
        - ```color``` is the colorization option. Either Color or Greyscale.
        - ```disposition``` is the paper disposition.
        - ```count``` is the number of copies to be printed.
        - ```stapling``` is the stapling options.
        - ```perforations``` is the perforation options.


    Parent class : User



    Methods:
        ```_compute_price``` compute the printing price
        ```_update_price``` update printing price
    """
    STATUS_AVAILABLE = (
            ('Pending', _('Pending')),
            ('Printable', _('Printable')),
            ('Running', _('Running')),
            ('Cancelled', _('Cancelled')),
            ('Finished', _('Finished'))
    )
    user = models.ForeignKey('users.User', on_delete=models.PROTECT)
    print_operation = models.ForeignKey('PrintOperation', on_delete=models.CASCADE)
    paid = models.BooleanField(default='False')
    file = models.FileField(
        storage=FileSystemStorage(location='/var/impressions'),
        upload_to=user_printing_path,
        validators=[FileValidator(
            allowed_types=ALLOWED_TYPES,
            max_size=MAX_PRINTFILE_SIZE)
        ],
        verbose_name=_('File')
    )
    filename = models.CharField(
        max_length=255,
        null=True,
        verbose_name=_('File Name')
    )
    starttime = models.DateTimeField(auto_now_add=True)
    endtime = models.DateTimeField(null=True)
    status = models.CharField(
        max_length=255,
        choices=STATUS_AVAILABLE,
        verbose_name=_('Status'),
        default='Pending'
    )
    printAs = models.ForeignKey(
        'users.User',
        on_delete=models.PROTECT,
        related_name='print_as_user',
        blank=True,
        null=True,
        verbose_name=_('Print as')
    )
    price = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name=_("Price"),
        default=0.0
    )
    pages = models.IntegerField(default=0)
    format = models.CharField(
        max_length=255,
        choices=FORMAT_AVAILABLE,
        default='A4',
        verbose_name=_("Format")
    )
    color = models.CharField(
        max_length=255,
        choices=COLOR_CHOICES,
        default='Greyscale',
        verbose_name=_("Color")
    )
    disposition = models.CharField(
        max_length=255,
        choices=DISPOSITIONS_AVAILABLE,
        default='TwoSided',
        verbose_name=_("Disposition")
    )
    count = models.PositiveIntegerField(
        default=1,
        verbose_name=_("Count")
    )
    stapling = models.CharField(
        max_length=255,
        choices=STAPLING_OPTIONS,
        default='None',
        verbose_name=_("Stapling")
    )
    perforation = models.CharField(
        max_length=255,
        choices=PERFORATION_OPTIONS,
        default='None',
        verbose_name=_("Perforation")
    )


    def _update_price(self):
        self.price = self._compute_price()

    def _compute_price(self):
        pages = int(self.pages)
        price_paper = PRICES[self.format]
        price_stapling = 0.0
        nb_staples = 0

        if self.disposition == 'Booklet':
            sheets = int((pages+3)/4)
            pages = 2 * sheets
        elif self.disposition == 'TwoSided':
            sheets = int(pages/2.+0.5)
        else:
            sheets = pages

        if self.format == 'A3':
            pages*=2

        price_ink = price_paper*sheets + PRICES[self.color]*pages

        if self.stapling:
            nb_staples = 2 - int('Top' in self.stapling)

        price_stapling = nb_staples * PRICES['Staples']

        total_price = math.floor(self.count * (price_ink + price_stapling))

        return total_price/100

    def can_view(self, user_request, *args, **kwargs):
        if user_request.has_perm('printer.view_jobwithoptions'):
            return True, None
        elif user_request == self.user or user_request == self.printAs:
            return True, None
        else:
            return False, _("This is not your print job")

    def can_edit(self, user_request, *args, **kwargs):
        if user_request.has_perm('printer.change_jobwithoptions'):
            return True, None
        elif user_request == self.user or user_request == self.printAs:
            return True, None
        else:
            return False, _("This is not your print operation job")

    def __init__(self, *args, **kwargs):
        super(JobWithOptions, self).__init__(*args, **kwargs)
        self.field_permissions = {
            'printAs': self.can_change_printas,
        }

    def can_change_printas(self, user_request, *_args, **_kwargs):
        return user_request.adherent.club_members.all(), None
   
    def save(self, *args, **kwargs):
        self._update_price()
        super(JobWithOptions, self).save(*args, **kwargs)

