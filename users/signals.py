"""
A set of signals used by users. Various classes in users emit these signals to signal the need to sync or
remove an object from optionnal authentication backends, e.g. LDAP.

* `users.signals.synchronise`:
    Expresses the need for an instance of a users class to be synchronised. `sender` and `instance` are
    always set. It is up to the receiver to ensure the others are set correctly if they make sense.
    Arguments:
        * `sender` : The model class.
        * `instance` : The actual instance being synchronised.
        * `base` : Default `True`. When `True`, synchronise basic attributes.
        * `access_refresh` : Default `True`. When `True`, synchronise the access time.
        * `mac_refresh` : Default `True`. When True, synchronise the list of mac addresses.
        * `group_refresh`: Default `False`. When `True` synchronise the groups of the instance.
* `users.signals.remove`:
    Expresses the need for an instance of a users class to be removed.
    Arguments:
        * `sender` : The model class.
        * `instance` : The actual instance being removed.
* `users.signals.remove_mass`:
    Same as `users.signals.remove` except it removes a queryset. For now it is only used by `users.models.User`.
    Arguments:
        * `sender` : The model class.
        * `queryset` : The actual instances being removed.

"""

import django.dispatch

synchronise = django.dispatch.Signal(
    providing_args=[
        "sender",
        "instance",
        "base",
        "access_refresh",
        "mac_refresh",
        "group_refresh",
    ]
)
remove = django.dispatch.Signal(providing_args=["sender", "instance"])
remove_mass = django.dispatch.Signal(providing_args=["sender", "queryset"])
