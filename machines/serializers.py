#Augustin Lemesle

from rest_framework import serializers
from machines.models import Interface, IpType

class InterfaceSerializer( serializers.ModelSerializer):
    class Meta:
        model = Interface
        fields = ('ipv4', 'mac_address', 'dns', 'type')

class TypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = IpType
        fields = ('type', 'extension')


