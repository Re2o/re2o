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

from machines.models import Interface
from topologie.models import Room, Port, Switch
from users.models import User

from re2o.settings import RADIUS_VLAN_DECISION

VLAN_NOK = RADIUS_VLAN_DECISION['VLAN_NOK']
VLAN_OK = RADIUS_VLAN_DECISION['VLAN_OK']

def decide_vlan(switch_name, port_number, mac_address):
        # Get port from switch and port number
        switch = Switch.objects.filter(switch_interface=Interface.objects.filter(dns=switch_name))
        if switch:
            port = Port.objects.filter(switch=switch[0], port=port_number)
            if port:
                port = port[0]
                if port.radius == 'NO':
                # Aucune authentification sur ce port
                    decision = ("Pas d'authentification sur ce port", VLAN_OK)
                elif port.radius == 'BLOQ':
                # Prise désactivée
                    decision = ('Port desactive', VLAN_NOK)
                elif port.radius == 'COMMON' or port.radius == 'STRICT':
		    # Authentification par mac
                    interface = Interface.objects.filter(mac_address=mac_address)
                    if not interface:
                        decision = ('Mac not found', VLAN_NOK)
                    elif interface[0].is_active():
                        # Verification de la prise
                        if port.radius == 'STRICT':
                            if port.room:
                                user = User.objects.filter(room=Room.objects.filter(name=port.room))
                                if not user:
                                    decision = ('Chambre non cotisante', VLAN_NOK)
                                elif user[0].has_access():
                                    decision = ('Machine OK, Proprio OK', VLAN_OK)
                            else:
                                decision = ('Chambre inconnue', VLAN_NOK)
                        else:
                            # Mode COMMON
                            decision = ('Machine OK', VLAN_OK)
                    else:
                        decision = ('Machine non active / adherent non cotisant', VLAN_NOK)
                else:
                    decision = ('VLAN forced', int(port.radius))
            else:
                decision = ('port not found!', VLAN_OK)
        else:
            decision = ('switch not found!', VLAN_OK)
        return decision

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Decide radius vlan attribution')
    parser.add_argument('switch_name', action="store")
    parser.add_argument('port_number', action="store", type=int)
    parser.add_argument('mac_address', action="store")
    args = parser.parse_args()
    print(decide_vlan(args.switch_name, args.port_number, args.mac_address))

