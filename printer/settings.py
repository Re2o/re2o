"""printer.settings
Define variables used in printer app
"""
from django.utils.translation import ugettext_lazy as _
from preferences.models import OptionalPrinter

settings, created  = OptionalPrinter.objects.get_or_create()

MAX_PRINTFILE_SIZE = settings.max_size * 1024 * 1024 # 25 MB
ALLOWED_TYPES = ['application/pdf']


A3_enabled = settings.A3_enabled
booklet_enabled = settings.booklet_enabled
color_enabled = settings.color_enabled
stapling_enabled = settings.stapling_enabled
perforation_enabled = settings.perforation_enabled

FORMAT_AVAILABLE = (
    ('A4', _('A4')),
    ('A3', _('A3')),
)
COLOR_CHOICES = (
    ('Greyscale', _('Greyscale')),
    ('Color', _('Color'))
)
DISPOSITIONS_AVAILABLE = (
    ('TwoSided', _('Two sided')),
    ('OneSided', _('One sided')),
    ('Booklet', _('Booklet'))
)
STAPLING_OPTIONS = (
    ('None', _('None')),
    ('TopLeft', _('One top left')),
    ('TopRight', _('One top right')),
    ('LeftSided', _('Two left sided')),
    ('RightSided', _('Two right sided'))
)
PERFORATION_OPTIONS = (
    ('None', _('None')),
    ('TwoLeftSidedHoles', _('Two left sided holes')),
    ('TwoRightSidedHoles', _('Two right sided holes')),
    ('TwoTopHoles', _('Two top holes')),
    ('TwoBottomHoles', _('Two bottom holes')),
    ('FourLeftSidedHoles', _('Four left sided holes')),
    ('FourRightSidedHoles', _('Four right sided holes'))
)


## Config

## Depreciation
depr = settings.depreciation_coef

PRICES = {
    'Depreciation': depr,
    'A3': settings.A3_price,
    'A4': settings.A4_price,
    'Color': settings.Color_price + depr,
    'Greyscale': settings.Greyscale_price + depr,
    'Staples': settings.Staples_price,
}
