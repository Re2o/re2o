from machines.models import Interface, Machine
from .settings import SITE_NAME

def context_user(request):
    user = request.user
    if user.is_authenticated():
        interfaces = user.user_interfaces()
    else:
        interfaces = None
    is_cableur = user.has_perms(('cableur',))
    is_bureau = user.has_perms(('bureau',))
    is_bofh = user.has_perms(('bofh',))
    is_trez = user.has_perms(('trésorier',))
    is_infra = user.has_perms(('infra',))
    return {
        'request_user': user,
        'is_cableur': is_cableur,
        'is_bureau': is_bureau,
        'is_bofh': is_bofh,
        'is_trez': is_trez,
        'is_infra': is_infra,
        'interfaces': interfaces,
        'site_name': SITE_NAME,
    }
