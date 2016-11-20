#Augustin Lemesle

from rest_framework import serializers
from machines.models import Interface, IpType, Extension, IpList, MachineType, Alias, Mx, Ns

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
    def to_representation(self, value):
        return value.alias

class MxSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField('get_alias_name')
    zone = serializers.SerializerMethodField('get_zone_name')

    class Meta:
        model = Mx
        fields = ('zone', 'priority', 'name')

    def get_alias_name(self, obj):
        return obj.name.alias + obj.name.extension.name

    def get_zone_name(self, obj):
        return obj.zone.name

class NsSerializer(serializers.ModelSerializer):
    zone = serializers.SerializerMethodField('get_zone_name')
    interface = serializers.SerializerMethodField('get_interface_name')

    class Meta:
        model = Ns
        fields = ('zone', 'interface')

    def get_zone_name(self, obj):
        return obj.zone.name

    def get_interface_name(self, obj):
        return obj.interface.dns + obj.interface.ipv4.ip_type.extension.name

class AliasSerializer(serializers.ModelSerializer):
    interface_parent = serializers.SerializerMethodField('get_interface_name')
    extension = serializers.SerializerMethodField('get_zone_name')

    class Meta:
        model = Alias
        fields = ('interface_parent', 'alias', 'extension')

    def get_zone_name(self, obj):
        return obj.extension.name 

    def get_interface_name(self, obj):
        return obj.interface_parent.dns + obj.interface_parent.ipv4.ip_type.extension.name
