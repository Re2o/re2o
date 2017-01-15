import os, sys

proj_path = "/var/www/re2o/"
# This is so Django knows where to find stuff.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "re2o.settings")
sys.path.append(proj_path)

# This is so my local_settings.py gets loaded.
os.chdir(proj_path)

# This is so models get loaded.
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

import argparse

from machines.models import Interface, IpList
from topologie.models import Room, Port, Switch
from users.models import User

from re2o.settings import RADIUS_VLAN_DECISION

VLAN_NOK = RADIUS_VLAN_DECISION['VLAN_NOK']
VLAN_OK = RADIUS_VLAN_DECISION['VLAN_OK']

def decide_vlan(switch_ip, port_number, mac_address):
    # Get port from switch and port number
    switch = Switch.objects.filter(switch_interface=Interface.objects.filter(ipv4=IpList.objects.filter(ipv4=switch_ip)))
    if not switch:
        return ('?', 'Switch inconnu', VLAN_OK)

    sw_name = str(switch[0].switch_interface)

    port = Port.objects.filter(switch=switch[0], port=port_number)
    if not port:
        return (sw_name, 'Port inconnu', VLAN_OK)

    port = port[0]

    if port.radius == 'NO':
        return (sw_name, "Pas d'authentification sur ce port", VLAN_OK)

    if port.radius == 'BLOQ':
        return (sw_name, 'Port desactive', VLAN_NOK)

    if port.radius == 'STRICT':
        if not port.room:
            return (sw_name, 'Chambre inconnue', VLAN_NOK)

        room_user = User.objects.filter(room=Room.objects.filter(name=port.room))
        if not room_user:
            return (sw_name, 'Chambre non cotisante', VLAN_NOK)
        elif not room_user[0].has_access():
            return (sw_name, 'Chambre resident desactive', VLAN_NOK)
        # else: user OK, on passe à la verif MAC

    if port.radius == 'COMMON' or port.radius == 'STRICT':
        # Authentification par mac
        interface = Interface.objects.filter(mac_address=mac_address)
        if not interface:
            return (sw_name, 'Machine inconnue', VLAN_NOK)
        elif not interface[0].is_active():
            return (sw_name, 'Machine non active / adherent non cotisant', VLAN_NOK)
        else:
            return (sw_name, 'Machine OK', VLAN_OK)

    # On gere bien tous les autres états possibles, il ne reste que le VLAN en dur
    return (sw_name, 'VLAN impose', int(port.radius))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Decide radius vlan attribution')
    parser.add_argument('switch_ip', action="store")
    parser.add_argument('port_number', action="store", type=int)
    parser.add_argument('mac_address', action="store")
    args = parser.parse_args()
    print(decide_vlan(args.switch_ip, args.port_number, args.mac_address))

