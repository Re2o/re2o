#Augustin Lemesle

from rest_framework import serializers
from machines.models import Interface, IpType, Extension, IpList, MachineType, Alias

class IpTypeField(serializers.RelatedField):
    def to_representation(self, value):
        return value.type

class IpListSerializer(serializers.ModelSerializer):
    ip_type = IpTypeField(read_only=True)

    class Meta:
        model = IpList
        fields = ('ipv4', 'ip_type')

class InterfaceSerializer(serializers.ModelSerializer):
    ipv4 = IpListSerializer(read_only=True)
   
    class Meta:
        model = Interface
        fields = ('ipv4', 'mac_address', 'dns')

class ExtensionNameField(serializers.RelatedField):
    def to_reprsentation(self, value):
        return value.name

class TypeSerializer(serializers.ModelSerializer):
    extension = ExtensionNameField(read_only=True)

    class Meta:
        model = IpType
        fields = ('type', 'extension', 'domaine_ip', 'domaine_range')

class IpList_ExtensionField(serializers.RelatedField):
    def to_representation(self, value):
        return value.ipv4.ip_type.extension.name

class InterfaceDNS_ExtensionSerializer(serializers.ModelSerializer):
    ipv4 = IpList_ExtensionField(read_only=True)

    class Meta:
        model = Interface
        fields = ('ipv4', 'dns')

class AliasSerializer(serializers.ModelSerializer):
    interface_parent = InterfaceDNS_ExtensionSerializer(read_only=True)
    extension = ExtensionNameField(read_only=True)

    class Meta:
        model = Alias
        fields = ('interface_parent', 'alias', 'extension')
