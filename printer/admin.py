# -*- coding: utf-8 -*-
"""printer.admin
The objects, fields and datastructures visible in the Django admin view
"""

from __future__ import unicode_literals

from django.contrib import admin
from reversion.admin import VersionAdmin

from .models import Digicode, PrintOperation, JobWithOptions



class DigicodeAdmin(VersionAdmin):
    """
    """
    pass

class PrintOperationAdmin(VersionAdmin):
    """
    """
    pass

class JobWithOptionsAdmin(VersionAdmin):
    """
    """
    pass


admin.site.register(Digicode, DigicodeAdmin)
admin.site.register(PrintOperation, PrintOperationAdmin)
admin.site.register(JobWithOptions, JobWithOptionsAdmin)
