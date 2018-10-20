"""printer.settings
Define variables used in printer app
"""

from preferences.models import OptionalPrinter

settings = OptionalPrinter.objects.get()

MAX_PRINTFILE_SIZE = settings.max_size * 1024 * 1024 # 25 MB
ALLOWED_TYPES = ['application/pdf']




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
