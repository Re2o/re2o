

def context_user(request):
    user = request.user
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
    }
