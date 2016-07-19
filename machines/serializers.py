from rest_framework import serializers
from machines.models import Interface

class InterfaceSerializer( serializers.ModelSerializer):
    class Meta:
        model = Interface
        fields = ('ipv4', 'mac_address', 'dns')



