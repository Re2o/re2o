from django import template
from re2o.settings_local import OPTIONNAL_LINK_RE2O

register = template.Library()

@register.simple_tag
def nav_link_nologin():
    template = """
    <li>
        <a href="{}">
            <i class="fa {}"></i> {}
        </a>
    </li>
    """
    res = ""
    for link in OPTIONNAL_LINK_RE2O:
        res += template.format(link[0],link[1],link[2])
    return res