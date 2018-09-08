# -*- mode: python; coding: utf-8 -*-


"""printer.validators
Custom validators useful for printer application.
Author : Maxime Bombar <bombar@crans.org>.
"""



from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError
from django.template.defaultfilters import filesizeformat
from django.utils.deconstruct import deconstructible

import mimetypes

@deconstructible
class FileValidator(object):
    """
    Custom validator for files. It checks the size and mimetype.
    
    Parameters:
       * ```allowed_types``` is an iterable of allowed mimetypes. Example: ['application/pdf'] for a pdf file.
       * ```max_size``` is the maximum size allowed in bytes. Example:  25*1024*1024 for 25 MB.

    Usage example:
    
        class UploadModel(models.Model):
            file = fileField(..., validators=FileValidator(allowed_types = ['application/pdf'], max_size=25*1024*1024))
    """


    def __init__(self, *args, **kwargs):
        """
        Initialize the custom validator. 
        By default, all types and size are allowed.
        """
        self.allowed_types = kwargs.pop('allowed_types', None)
        self.max_size = kwargs.pop('max_size', None)

    def __call__(self, value):
        """
        Check the type and size.
        """

        
        type_message = _("MIME type '%(type)s' is not valid. Please, use one of these types: %(allowed_types)s.")
        type_code = 'invalidType'
        
        oversized_message = _('The current file size is %(size)s. The maximum file size is %(max_size)s.')
        oversized_code = 'oversized'

        
        mimetype = mimetypes.guess_type(value.name)[0]
        if self.allowed_types and not (mimetype in self.allowed_types):
            type_params = {
                'type': mimetype,
                'allowed_types': ', '.join(self.allowed_types),
                }

            raise ValidationError(type_message, code=type_code, params=type_params)

        filesize = len(value)
        if self.max_size and filesize > self.max_size:
            oversized_params = {
                'size': '{}'.format(filesizeformat(filesize)),
                'max_size': '{}'.format(filesizeformat(self.max_size)),
                }

            raise ValidationError(oversized_message, code=oversized_code, params=oversized_params)
