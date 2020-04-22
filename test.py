from reversion.models import Version
from machines.models import IpList
from machines.models import Interface
from machines.models import Machine
from users.models import User


def get_interfaces_with_ip(ip):
    """
    Get all the interfaces that, at some point, had the given ip
    """
    # TODO: What if IpList was deleted?
    ip_id = IpList.objects.get(ipv4=ip).id
    interfaces = Version.objects.get_for_model(Interface)
    interfaces = filter(lambda x: x.field_dict["ipv4_id"] == ip_id, interfaces)
    return interfaces


def get_machine_with_interface(interface):
    """
    Get the machine which contained the given interface, even if deleted
    """
    machine_id = interface.field_dict["machine_id"]
    machines = Version.objects.get_for_model(Machine)
    machines = filter(lambda x: x.field_dict["id"] == machine_id, machines)
    return machines[0]


def get_user_with_machine(machine):
    """
    """
    user_id = machine.field_dict["user_id"]
    user = User.objects.filter(id=user_id)
    return user[0]


interfaces = get_interfaces_with_ip("10.0.0.0")

output_dict = {}
for interface in interfaces:
    mac = interface.field_dict["mac_address"]
    machine = get_machine_with_interface(interface)
    user = get_user_with_machine(machine)
    output_dict[mac] = {
        "machine": machine.field_dict["name"],
        "user": user
    }

print(output_dict)

