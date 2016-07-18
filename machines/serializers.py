from rest_framework import serializers
from machines.models import Interface

class InterfaceSerializer( serializers.ModelSerializer):
    class Meta:
        model = Interface
        fields = ('id','ipv4', 'mac_address')


