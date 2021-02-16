"""
Templatetags for fontawesome
"""
from django import template
from django.conf import settings
from django.templatetags.static import static

register = template.Library()

@register.simple_tag
def font_awesome_url():
    """Return the font awesome url depending on the use of a CDN.

    Returns:
        string: url of the font-awesome css file
    """
    if settings.USE_CDN:
        return "https://pro.fontawesome.com/releases/v5.10.0/css/all.css"
    else:
        return static("css/font-awesome.min.css")