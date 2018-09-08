




"""printer.settings
Define variables, to be changed into a configuration table.
"""



MAX_PRINTFILE_SIZE = 25 * 1024 * 1024 # 25 MB
ALLOWED_TYPES = ['application/pdf']




## Config

## Depreciation
depr = 2.16

PRICES = {
    'Depreciation': depr,
    'A3': 0.670,
    'A4': 2.1504,
    'Color': 9.0 + depr,
    'Greyscale': 0.9 + depr,
    'Staples': 1.3333,
}
