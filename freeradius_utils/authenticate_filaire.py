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
        if switch:
            sw_name = str(switch[0].switch_interface)
            port = Port.objects.filter(switch=switch[0], port=port_number)
            if port:
                port = port[0]
                if port.radius == 'NO':
                # Aucune authentification sur ce port
                    decision = (sw_name, "Pas d'authentification sur ce port", VLAN_OK)
                elif port.radius == 'BLOQ':
                    # Prise désactivée
                    decision = (sw_name, 'Port desactive', VLAN_NOK)
                elif port.radius == 'COMMON':
		    # Authentification par mac
                    interface = Interface.objects.filter(mac_address=mac_address)
                    if not interface:
                        decision = (sw_name, 'Mac not found', VLAN_NOK)
                    elif not interface[0].is_active():
                        decision = (sw_name, 'Machine non active / adherent non cotisant', VLAN_NOK)
                    else:
                        decision = (sw_name, 'Machine OK', VLAN_OK)
                elif port.radius == 'STRICT':
                    if port.room:
                        user = User.objects.filter(room=Room.objects.filter(name=port.room))
                        if not user:
                            decision = (sw_name, 'Chambre non cotisante', VLAN_NOK)
                        elif not user[0].has_access():
                            decision = (sw_name, 'Resident desactive', VLAN_NOK)
                        else:
                            # Verification de la mac
                            interface = Interface.objects.filter(mac_address=mac_address)
                            if not interface:
                                decision = (sw_name, 'Chambre Ok, but mac not found', VLAN_NOK)
                            elif not interface[0].is_active():
                                decision = (sw_name, 'Chambre Ok, but machine non active / adherent non cotisant', VLAN_NOK)
                            else:
                                decision = (sw_name, 'Machine OK, Proprio OK', VLAN_OK)
                    else:
                        decision = (sw_name, 'Chambre inconnue', VLAN_NOK)
                else:
                    decision = (sw_name, 'VLAN forced', int(port.radius))
            else:
                decision = (sw_name, 'port not found!', VLAN_OK)
        else:
            decision = ('?', 'switch not found!', VLAN_OK)
        return decision

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Decide radius vlan attribution')
    parser.add_argument('switch_ip', action="store")
    parser.add_argument('port_number', action="store", type=int)
    parser.add_argument('mac_address', action="store")
    args = parser.parse_args()
    print(decide_vlan(args.switch_ip, args.port_number, args.mac_address))

