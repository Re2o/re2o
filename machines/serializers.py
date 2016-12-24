#Augustin Lemesle

from rest_framework import serializers
from machines.models import Interface, IpType, Extension, IpList, MachineType, Domain, Mx, Ns

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
    mac_address = serializers.SerializerMethodField('get_macaddress')
    dns = serializers.SerializerMethodField('get_dns')

    class Meta:
        model = Interface
        fields = ('ipv4', 'mac_address')

    def get_dns(self, obj):
        return obj.domain_set.all().first()

    def get_macaddress(self, obj):
        return str(obj.mac_address)

class ExtensionNameField(serializers.RelatedField):
    def to_representation(self, value):
        return value.name

class TypeSerializer(serializers.ModelSerializer):
    extension = ExtensionNameField(read_only=True)

    class Meta:
        model = IpType
        fields = ('type', 'extension', 'domaine_ip', 'domaine_range')

class ExtensionSerializer(serializers.ModelSerializer):
    origin = serializers.SerializerMethodField('get_origin_ip')

    class Meta:
        model = Extension
        fields = ('name', 'origin')

    def get_origin_ip(self, obj):
        return obj.origin.ipv4

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

class DomainSerializer(serializers.ModelSerializer):
    interface_parent = serializers.SerializerMethodField('get_interface_name')
    extension = serializers.SerializerMethodField('get_zone_name')
    cname = serializers.SerializerMethodField('get_cname')

    class Meta:
        model = Domain
        fields = ('interface_parent', 'name', 'extension', 'cname')

    def get_zone_name(self, obj):
        return obj.extension.name 

    def get_cname(self, obj):
        return obj.cname.name + obj.cname.extension.name

    def get_interface_name(self, obj):
        return obj.name + obj.extension.name
