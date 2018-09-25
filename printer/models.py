# -*- mode: python; coding: utf-8 -*-

"""printer.models
Models of the printer application
Author : Maxime Bombar <bombar@crans.org>.
"""

from __future__ import unicode_literals

from django.db import models
from django.forms import ValidationError
from django.utils.translation import ugettext_lazy as _
from django.template.defaultfilters import filesizeformat

from re2o.mixins import RevMixin

import users.models

from .validators import (
    FileValidator,
)

from .settings import (
    MAX_PRINTFILE_SIZE,
    ALLOWED_TYPES,
    PRICES,
)

from .utils import user_printing_path

import math

"""
- ```user_printing_path``` is a function that returns the path of the uploaded file, used with the FileField.
- ```Job``` is the main model of a printer job. His parent is the ```user``` model.
"""



class JobWithOptions(RevMixin, models.Model):
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
            ('Printable', 'Printable'),
            ('Running', 'Running'),
            ('Cancelled', 'Cancelled'),
            ('Finished', 'Finished')
        )
        user = models.ForeignKey('users.User', on_delete=models.PROTECT)
        file = models.FileField(upload_to=user_printing_path, validators=[FileValidator(allowed_types=ALLOWED_TYPES, max_size=MAX_PRINTFILE_SIZE)])
        filename = models.CharField(max_length=255,null=True)
        starttime = models.DateTimeField(auto_now_add=True)
        endtime = models.DateTimeField(null=True)
        status = models.CharField(max_length=255, choices=STATUS_AVAILABLE)
        printAs = models.ForeignKey('users.User', on_delete=models.PROTECT, related_name='print_as_user', blank=True, null=True)
        price = models.DecimalField(
            max_digits=5,
            decimal_places=2,
            verbose_name=_("price"),
            default=0.0)
        pages = models.IntegerField(default=0)
        FORMAT_AVAILABLE = (
            ('A4', 'A4'),
            ('A3', 'A3'),
        )
        COLOR_CHOICES = (
            ('Greyscale', 'Greyscale'),
            ('Color', 'Color')
        )
        DISPOSITIONS_AVAILABLE = (
            ('TwoSided', 'Two sided'),
            ('OneSided', 'One sided'),
            ('Booklet', 'Booklet')
        )
        STAPLING_OPTIONS = (
            ('None', 'None'),
            ('TopLeft', 'One top left'),
            ('TopRight', 'One top right'),
            ('LeftSided', 'Two left sided'),
            ('RightSided', 'Two right sided')
        )
        PERFORATION_OPTIONS = (
            ('None', 'None'),
            ('TwoLeftSidedHoles', 'Two left sided holes'),
            ('TwoRightSidedHoles', 'Two right sided holes'),
            ('TwoTopHoles', 'Two top holes'),
            ('TwoBottomHoles', 'Two bottom holes'),
            ('FourLeftSidedHoles', 'Four left sided holes'),
            ('FourRightSidedHoles', 'Four right sided holes')
        )

        format = models.CharField(max_length=255, choices=FORMAT_AVAILABLE, default='A4')
        color = models.CharField(max_length=255, choices=COLOR_CHOICES, default='Greyscale')
        disposition = models.CharField(max_length=255, choices=DISPOSITIONS_AVAILABLE, default='TwoSided')
        count = models.PositiveIntegerField(default=1)
        stapling = models.CharField(max_length=255, choices=STAPLING_OPTIONS, default='None')
        perforation = models.CharField(max_length=255, choices=PERFORATION_OPTIONS, default='None')


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

            return float(total_price)/100
