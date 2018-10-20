"""printer.settings
Define variables used in printer app
"""

from preferences.models import OptionalPrinter

settings = OptionalPrinter.objects.get()

MAX_PRINTFILE_SIZE = settings.max_size * 1024 * 1024 # 25 MB
ALLOWED_TYPES = ['application/pdf']


A3_enabled = settings.A3_enabled
booklet_enabled = settings.booklet_enabled
color_enabled = settings.color_enabled
stapling_enabled = settings.stapling_enabled
perforation_enabled = settings.perforation_enabled

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
