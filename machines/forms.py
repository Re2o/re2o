# -*- mode: python; coding: utf-8 -*-
# Re2o est un logiciel d'administration développé initiallement au Rézo Metz. Il
# se veut agnostique au réseau considéré, de manière à être installable en
# quelques clics.
#
# Copyright © 2017  Gabriel Détraz
# Copyright © 2017  Lara Kermarec
# Copyright © 2017  Augustin Lemesle
# Copyright © 2017  Maël Kervella
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
"""
Forms to create, edit and delete:
    * machines
    * interfaces
    * domains (machine names)
    * aliases (CNAME)
    * services (DHCP, DNS...)
    * NS records (DNS server)
    * MX records (mail serveur)
    * open ports and ports opening for interfaces
"""

from __future__ import unicode_literals

from django import forms
from django.forms import ModelForm, Form
from django.utils.translation import ugettext_lazy as _

from re2o.field_permissions import FieldPermissionFormMixin
from re2o.mixins import FormRevMixin, AutocompleteModelMixin, AutocompleteMultipleModelMixin
from .models import (
    Domain,
    Machine,
    Interface,
    IpList,
    MachineType,
    Extension,
    SOA,
    Mx,
    Txt,
    DName,
    Ns,
    Role,
    Service,
    Vlan,
    Srv,
    SshFp,
    Nas,
    IpType,
    OuverturePortList,
    Ipv6List,
)


class EditMachineForm(FormRevMixin, FieldPermissionFormMixin, ModelForm):
    """Form used to edit a machine."""

    class Meta:
        model = Machine
        fields = "__all__"
        widgets = {
            "user": AutocompleteModelMixin(
                url="/users/user-autocomplete",
            ),
        }

    def __init__(self, *args, **kwargs):
        prefix = kwargs.pop("prefix", self.Meta.model.__name__)
        super(EditMachineForm, self).__init__(*args, prefix=prefix, **kwargs)
        self.fields["name"].label = _("Machine name")


class NewMachineForm(EditMachineForm):
    """Form used to create a machine."""

    class Meta(EditMachineForm.Meta):
        fields = ["name"]


class EditInterfaceForm(FormRevMixin, FieldPermissionFormMixin, ModelForm):
    """Form used to edit an interface."""

    class Meta:
        model = Interface
        fields = ["machine", "machine_type", "ipv4", "mac_address", "details"]
        widgets = {
            "machine": AutocompleteModelMixin(
                url="/machines/machine-autocomplete",
            ),
            "machine_type": AutocompleteModelMixin(
                url="/machines/machinetype-autocomplete",
            ),
            "ipv4": AutocompleteModelMixin(
                url="/machines/iplist-autocomplete", forward=['machine_type'],
                attrs={
                'data-placeholder': 'Automatic assigment. Type to choose specific ip.',
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        prefix = kwargs.pop("prefix", self.Meta.model.__name__)
        user = kwargs.get("user")
        super(EditInterfaceForm, self).__init__(*args, prefix=prefix, **kwargs)
        self.fields["mac_address"].label = _("MAC address")
        self.fields["machine_type"].label = _("Machine type")
        self.fields["machine_type"].empty_label = _("Select a machine type")
        if "ipv4" in self.fields:
            self.fields["ipv4"].empty_label = _("Automatic IPv4 assignment")
            self.fields["ipv4"].queryset = IpList.objects.filter(interface__isnull=True)
            can_use_all_iptype, _reason, _permissions = IpType.can_use_all(user)
            if not can_use_all_iptype:
                self.fields["ipv4"].queryset = IpList.objects.filter(
                    interface__isnull=True
                ).filter(ip_type__in=IpType.objects.filter(need_infra=False))
            else:
                self.fields["ipv4"].queryset = IpList.objects.filter(
                    interface__isnull=True
                )
            # Add it's own address
            self.fields["ipv4"].queryset |= IpList.objects.filter(
                interface=self.instance
            )
        if "machine" in self.fields:
            self.fields["machine"].queryset = Machine.objects.all().select_related(
                "user"
            )
        can_use_all_machinetype, _reason, _permissions = MachineType.can_use_all(user)
        if not can_use_all_machinetype:
            self.fields["machine_type"].queryset = MachineType.objects.filter(
                ip_type__in=IpType.objects.filter(need_infra=False)
            )


class AddInterfaceForm(EditInterfaceForm):
    """Form used to add an interface to a machine."""

    class Meta(EditInterfaceForm.Meta):
        fields = ["machine_type", "ipv4", "mac_address", "details"]


class AliasForm(FormRevMixin, FieldPermissionFormMixin, ModelForm):
    """Form used to add and edit an alias (CNAME)."""

    class Meta:
        model = Domain
        fields = ["name", "extension", "ttl"]
        widgets = {
            "extension": AutocompleteModelMixin(
                url="/machines/extension-autocomplete",
            ),
        }

    def __init__(self, *args, **kwargs):
        prefix = kwargs.pop("prefix", self.Meta.model.__name__)
        user = kwargs["user"]
        super(AliasForm, self).__init__(*args, prefix=prefix, **kwargs)
        can_use_all, _reason, _permissions = Extension.can_use_all(user)
        if not can_use_all:
            self.fields["extension"].queryset = Extension.objects.filter(
                need_infra=False
            )


class DomainForm(FormRevMixin, FieldPermissionFormMixin, ModelForm):
    """Form used to add and edit a domain record, related to an
    interface.
    """

    class Meta:
        model = Domain
        fields = ["name", "ttl"]

    def __init__(self, *args, **kwargs):
        prefix = kwargs.pop("prefix", self.Meta.model.__name__)
        super(DomainForm, self).__init__(*args, prefix=prefix, **kwargs)


class DelAliasForm(FormRevMixin, Form):
    """Form used to delete one or several aliases."""

    alias = forms.ModelMultipleChoiceField(
        queryset=Domain.objects.all(),
        label=_("Current aliases"),
        widget=forms.CheckboxSelectMultiple,
    )

    def __init__(self, *args, **kwargs):
        interface = kwargs.pop("interface")
        super(DelAliasForm, self).__init__(*args, **kwargs)
        self.fields["alias"].queryset = Domain.objects.filter(
            cname__in=Domain.objects.filter(interface_parent=interface)
        )


class MachineTypeForm(FormRevMixin, ModelForm):
    """Form used to add and edit a machine type, related to an IP type."""

    class Meta:
        model = MachineType
        fields = ["name", "ip_type"]
        widgets = {
            "ip_type": AutocompleteModelMixin(
                url="/machines/iptype-autocomplete",
            ),
        }

    def __init__(self, *args, **kwargs):
        prefix = kwargs.pop("prefix", self.Meta.model.__name__)
        super(MachineTypeForm, self).__init__(*args, prefix=prefix, **kwargs)
        self.fields["name"].label = _("Machine type to add")
        self.fields["ip_type"].label = _("Related IP type")


class DelMachineTypeForm(FormRevMixin, Form):
    """Form used to delete one or several machines types."""

    machinetypes = forms.ModelMultipleChoiceField(
        queryset=MachineType.objects.none(),
        label=_("Current machine types"),
        widget=forms.CheckboxSelectMultiple,
    )

    def __init__(self, *args, **kwargs):
        instances = kwargs.pop("instances", None)
        super(DelMachineTypeForm, self).__init__(*args, **kwargs)
        if instances:
            self.fields["machinetypes"].queryset = instances
        else:
            self.fields["machinetypes"].queryset = MachineType.objects.all()


class IpTypeForm(FormRevMixin, ModelForm):
    """Form used to add an IP type. The start and stop IP addresses cannot
    be changed afterwards.
    """

    class Meta:
        model = IpType
        fields = "__all__"
        widgets = {
            "vlan": AutocompleteModelMixin(
                url="/machines/vlan-autocomplete",
            ),
            "extension": AutocompleteModelMixin(
                url="/machines/extension-autocomplete",
            ),
            "ouverture_ports": AutocompleteModelMixin(
                url="/machines/ouvertureportlist-autocomplete",
            ),
        }

    def __init__(self, *args, **kwargs):
        prefix = kwargs.pop("prefix", self.Meta.model.__name__)
        super(IpTypeForm, self).__init__(*args, prefix=prefix, **kwargs)
        self.fields["name"].label = _("IP type to add")


class EditIpTypeForm(IpTypeForm):
    """Form used to edit an IP type. The start and stop IP addresses cannot
    be changed.
    """

    class Meta(IpTypeForm.Meta):
        fields = [
            "extension",
            "name",
            "need_infra",
            "domaine_ip_network",
            "domaine_ip_netmask",
            "prefix_v6",
            "prefix_v6_length",
            "vlan",
            "reverse_v4",
            "reverse_v6",
            "ouverture_ports",
        ]


class DelIpTypeForm(FormRevMixin, Form):
    """Form used to delete one or several IP types."""

    iptypes = forms.ModelMultipleChoiceField(
        queryset=IpType.objects.none(),
        label=_("Current IP types"),
        widget=forms.CheckboxSelectMultiple,
    )

    def __init__(self, *args, **kwargs):
        instances = kwargs.pop("instances", None)
        super(DelIpTypeForm, self).__init__(*args, **kwargs)
        if instances:
            self.fields["iptypes"].queryset = instances
        else:
            self.fields["iptypes"].queryset = IpType.objects.all()


class ExtensionForm(FormRevMixin, ModelForm):
    """Form used to add and edit extensions."""

    class Meta:
        model = Extension
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        prefix = kwargs.pop("prefix", self.Meta.model.__name__)
        super(ExtensionForm, self).__init__(*args, prefix=prefix, **kwargs)
        self.fields["name"].label = _("Extension to add")
        self.fields["origin"].label = _("A record origin")
        self.fields["origin_v6"].label = _("AAAA record origin")
        self.fields["soa"].label = _("SOA record to use")
        self.fields["dnssec"].label = _("Sign with DNSSEC")


class DelExtensionForm(FormRevMixin, Form):
    """Form used to delete one or several extensions."""

    extensions = forms.ModelMultipleChoiceField(
        queryset=Extension.objects.none(),
        label=_("Current extensions"),
        widget=forms.CheckboxSelectMultiple,
    )

    def __init__(self, *args, **kwargs):
        instances = kwargs.pop("instances", None)
        super(DelExtensionForm, self).__init__(*args, **kwargs)
        if instances:
            self.fields["extensions"].queryset = instances
        else:
            self.fields["extensions"].queryset = Extension.objects.all()


class Ipv6ListForm(FormRevMixin, FieldPermissionFormMixin, ModelForm):
    """Form used to manage lists of IPv6 addresses."""

    class Meta:
        model = Ipv6List
        fields = ["ipv6", "slaac_ip", "active"]

    def __init__(self, *args, **kwargs):
        prefix = kwargs.pop("prefix", self.Meta.model.__name__)
        super(Ipv6ListForm, self).__init__(*args, prefix=prefix, **kwargs)


class SOAForm(FormRevMixin, ModelForm):
    """Form used to add and edit SOA records."""

    class Meta:
        model = SOA
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        prefix = kwargs.pop("prefix", self.Meta.model.__name__)
        super(SOAForm, self).__init__(*args, prefix=prefix, **kwargs)


class DelSOAForm(FormRevMixin, Form):
    """Form used to delete one or several SOA records."""

    soa = forms.ModelMultipleChoiceField(
        queryset=SOA.objects.none(),
        label=_("Current SOA records"),
        widget=forms.CheckboxSelectMultiple,
    )

    def __init__(self, *args, **kwargs):
        instances = kwargs.pop("instances", None)
        super(DelSOAForm, self).__init__(*args, **kwargs)
        if instances:
            self.fields["soa"].queryset = instances
        else:
            self.fields["soa"].queryset = SOA.objects.all()


class MxForm(FormRevMixin, ModelForm):
    """Form used to add and edit MX records."""

    class Meta:
        model = Mx
        fields = ["zone", "priority", "name", "ttl"]
        widgets = {
            "zone": AutocompleteModelMixin(
                url="/machines/extension-autocomplete",
            ),
            "name": AutocompleteModelMixin(
                url="/machines/domain-autocomplete",
            ),
        }

    def __init__(self, *args, **kwargs):
        prefix = kwargs.pop("prefix", self.Meta.model.__name__)
        super(MxForm, self).__init__(*args, prefix=prefix, **kwargs)
        self.fields["name"].queryset = Domain.objects.exclude(
            interface_parent=None
        ).select_related("extension")


class DelMxForm(FormRevMixin, Form):
    """Form used to delete one or several MX records."""

    mx = forms.ModelMultipleChoiceField(
        queryset=Mx.objects.none(),
        label=_("Current MX records"),
        widget=forms.CheckboxSelectMultiple,
    )

    def __init__(self, *args, **kwargs):
        instances = kwargs.pop("instances", None)
        super(DelMxForm, self).__init__(*args, **kwargs)
        if instances:
            self.fields["mx"].queryset = instances
        else:
            self.fields["mx"].queryset = Mx.objects.all()


class NsForm(FormRevMixin, ModelForm):
    """Form used to add and edit NS records. Only interface names are
    available because CNAME aliases should not be used in the records.
    """

    class Meta:
        model = Ns
        fields = ["zone", "ns", "ttl"]
        widgets = {
            "zone": AutocompleteModelMixin(
                url="/machines/extension-autocomplete",
            ),
            "ns": AutocompleteModelMixin(
                url="/machines/domain-autocomplete",
            ),
        }

    def __init__(self, *args, **kwargs):
        prefix = kwargs.pop("prefix", self.Meta.model.__name__)
        super(NsForm, self).__init__(*args, prefix=prefix, **kwargs)
        self.fields["ns"].queryset = Domain.objects.exclude(
            interface_parent=None
        ).select_related("extension")


class DelNsForm(FormRevMixin, Form):
    """Form used to delete one or several NS records."""

    nss = forms.ModelMultipleChoiceField(
        queryset=Ns.objects.none(),
        label=_("Current NS records"),
        widget=forms.CheckboxSelectMultiple,
    )

    def __init__(self, *args, **kwargs):
        instances = kwargs.pop("instances", None)
        super(DelNsForm, self).__init__(*args, **kwargs)
        if instances:
            self.fields["nss"].queryset = instances
        else:
            self.fields["nss"].queryset = Ns.objects.all()


class TxtForm(FormRevMixin, ModelForm):
    """Form used to add and edit TXT records."""

    class Meta:
        model = Txt
        fields = "__all__"
        widgets = {
            "zone": AutocompleteModelMixin(
                url="/machines/extension-autocomplete",
            ),
        }

    def __init__(self, *args, **kwargs):
        prefix = kwargs.pop("prefix", self.Meta.model.__name__)
        super(TxtForm, self).__init__(*args, prefix=prefix, **kwargs)


class DelTxtForm(FormRevMixin, Form):
    """Form used to delete one or several TXT records."""

    txt = forms.ModelMultipleChoiceField(
        queryset=Txt.objects.none(),
        label=_("Current TXT records"),
        widget=forms.CheckboxSelectMultiple,
    )

    def __init__(self, *args, **kwargs):
        instances = kwargs.pop("instances", None)
        super(DelTxtForm, self).__init__(*args, **kwargs)
        if instances:
            self.fields["txt"].queryset = instances
        else:
            self.fields["txt"].queryset = Txt.objects.all()


class DNameForm(FormRevMixin, ModelForm):
    """Form used to add and edit DNAME records."""

    class Meta:
        model = DName
        fields = "__all__"
        widgets = {
            "zone": AutocompleteModelMixin(
                url="/machines/extension-autocomplete",
            ),
        }

    def __init__(self, *args, **kwargs):
        prefix = kwargs.pop("prefix", self.Meta.model.__name__)
        super(DNameForm, self).__init__(*args, prefix=prefix, **kwargs)


class DelDNameForm(FormRevMixin, Form):
    """Form used to delete one or several DNAME records."""

    dnames = forms.ModelMultipleChoiceField(
        queryset=Txt.objects.none(),
        label=_("Current DNAME records"),
        widget=forms.CheckboxSelectMultiple,
    )

    def __init__(self, *args, **kwargs):
        instances = kwargs.pop("instances", None)
        super(DelDNameForm, self).__init__(*args, **kwargs)
        if instances:
            self.fields["dnames"].queryset = instances
        else:
            self.fields["dnames"].queryset = DName.objects.all()


class SrvForm(FormRevMixin, ModelForm):
    """Form used to add and edit SRV records."""

    class Meta:
        model = Srv
        fields = "__all__"
        widgets = {
            "extension": AutocompleteModelMixin(
                url="/machines/extension-autocomplete",
            ),
            "target": AutocompleteModelMixin(
                url="/machines/domain-autocomplete",
            ),
        }

    def __init__(self, *args, **kwargs):
        prefix = kwargs.pop("prefix", self.Meta.model.__name__)
        super(SrvForm, self).__init__(*args, prefix=prefix, **kwargs)


class DelSrvForm(FormRevMixin, Form):
    """Form used to delete one or several SRV records."""

    srv = forms.ModelMultipleChoiceField(
        queryset=Srv.objects.none(),
        label=_("Current SRV records"),
        widget=forms.CheckboxSelectMultiple,
    )

    def __init__(self, *args, **kwargs):
        instances = kwargs.pop("instances", None)
        super(DelSrvForm, self).__init__(*args, **kwargs)
        if instances:
            self.fields["srv"].queryset = instances
        else:
            self.fields["srv"].queryset = Srv.objects.all()


class NasForm(FormRevMixin, ModelForm):
    """Form used to create and edit NAS devices."""

    class Meta:
        model = Nas
        fields = "__all__"
        widgets = {
            "nas_type": AutocompleteModelMixin(
                url="/machines/machinetype-autocomplete",
            ),
            "machine_type": AutocompleteModelMixin(
                url="/machines/machinetype-autocomplete",
            ),
        }

    def __init__(self, *args, **kwargs):
        prefix = kwargs.pop("prefix", self.Meta.model.__name__)
        super(NasForm, self).__init__(*args, prefix=prefix, **kwargs)


class DelNasForm(FormRevMixin, Form):
    """Form used to delete one or several NAS devices."""

    nas = forms.ModelMultipleChoiceField(
        queryset=Nas.objects.none(),
        label=_("Current NAS devices"),
        widget=forms.CheckboxSelectMultiple,
    )

    def __init__(self, *args, **kwargs):
        instances = kwargs.pop("instances", None)
        super(DelNasForm, self).__init__(*args, **kwargs)
        if instances:
            self.fields["nas"].queryset = instances
        else:
            self.fields["nas"].queryset = Nas.objects.all()


class RoleForm(FormRevMixin, ModelForm):
    """Form used to add and edit roles."""

    class Meta:
        model = Role
        fields = "__all__"
        widgets = {
            "servers": AutocompleteMultipleModelMixin(
                url="/machines/interface-autocomplete",
            ),
        }

    def __init__(self, *args, **kwargs):
        prefix = kwargs.pop("prefix", self.Meta.model.__name__)
        super(RoleForm, self).__init__(*args, prefix=prefix, **kwargs)
        self.fields["servers"].queryset = Interface.objects.all().select_related(
            "domain__extension"
        )


class DelRoleForm(FormRevMixin, Form):
    """Form used to delete one or several roles."""

    role = forms.ModelMultipleChoiceField(
        queryset=Role.objects.none(),
        label=_("Current roles"),
        widget=forms.CheckboxSelectMultiple,
    )

    def __init__(self, *args, **kwargs):
        instances = kwargs.pop("instances", None)
        super(DelRoleForm, self).__init__(*args, **kwargs)
        if instances:
            self.fields["role"].queryset = instances
        else:
            self.fields["role"].queryset = Role.objects.all()


class ServiceForm(FormRevMixin, ModelForm):
    """Form to add and edit services (DHCP, DNS etc.)."""

    class Meta:
        model = Service
        fields = "__all__"
        widgets = {
            "servers": AutocompleteMultipleModelMixin(
                url="/machines/interface-autocomplete",
            ),
        }

    def __init__(self, *args, **kwargs):
        prefix = kwargs.pop("prefix", self.Meta.model.__name__)
        super(ServiceForm, self).__init__(*args, prefix=prefix, **kwargs)
        self.fields["servers"].queryset = Interface.objects.all().select_related(
            "domain__extension"
        )

    def save(self, commit=True):
        # TODO : None of the parents of ServiceForm use the commit
        # parameter in .save()
        instance = super(ServiceForm, self).save(commit=False)
        if commit:
            instance.save()
        instance.process_link(self.cleaned_data.get("servers"))
        return instance


class DelServiceForm(FormRevMixin, Form):
    """Form used to delete one or several services."""

    service = forms.ModelMultipleChoiceField(
        queryset=Service.objects.none(),
        label=_("Current services"),
        widget=forms.CheckboxSelectMultiple,
    )

    def __init__(self, *args, **kwargs):
        instances = kwargs.pop("instances", None)
        super(DelServiceForm, self).__init__(*args, **kwargs)
        if instances:
            self.fields["service"].queryset = instances
        else:
            self.fields["service"].queryset = Service.objects.all()


class VlanForm(FormRevMixin, ModelForm):
    """Form used to add and edit VLANs."""

    class Meta:
        model = Vlan
        fields = ["vlan_id", "name", "comment"]

    def __init__(self, *args, **kwargs):
        prefix = kwargs.pop("prefix", self.Meta.model.__name__)
        super(VlanForm, self).__init__(*args, prefix=prefix, **kwargs)


class EditOptionVlanForm(FormRevMixin, ModelForm):
    """Form used to edit the options of a VLAN."""

    class Meta:
        model = Vlan
        fields = ["dhcp_snooping", "dhcpv6_snooping", "arp_protect", "igmp", "mld"]

    def __init__(self, *args, **kwargs):
        prefix = kwargs.pop("prefix", self.Meta.model.__name__)
        super(EditOptionVlanForm, self).__init__(*args, prefix=prefix, **kwargs)


class DelVlanForm(FormRevMixin, Form):
    """Form used to delete one or several VLANs."""

    vlan = forms.ModelMultipleChoiceField(
        queryset=Vlan.objects.none(),
        label=_("Current VLANs"),
        widget=forms.CheckboxSelectMultiple,
    )

    def __init__(self, *args, **kwargs):
        instances = kwargs.pop("instances", None)
        super(DelVlanForm, self).__init__(*args, **kwargs)
        if instances:
            self.fields["vlan"].queryset = instances
        else:
            self.fields["vlan"].queryset = Vlan.objects.all()


class EditOuverturePortConfigForm(FormRevMixin, ModelForm):
    """Form to edit the ports opening list of an interface."""

    class Meta:
        model = Interface
        fields = ["port_lists"]
        widgets = {
            "port_lists": AutocompleteMultipleModelMixin(
                url="/machines/ouvertureportlist-autocomplete",
            ),
        }

    def __init__(self, *args, **kwargs):
        prefix = kwargs.pop("prefix", self.Meta.model.__name__)
        super(EditOuverturePortConfigForm, self).__init__(
            *args, prefix=prefix, **kwargs
        )


class EditOuverturePortListForm(FormRevMixin, ModelForm):
    """Form used to add and edit ports opening lists."""

    class Meta:
        model = OuverturePortList
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        prefix = kwargs.pop("prefix", self.Meta.model.__name__)
        super(EditOuverturePortListForm, self).__init__(*args, prefix=prefix, **kwargs)


class SshFpForm(FormRevMixin, ModelForm):
    """Form used to add and edit SSHFP records."""

    class Meta:
        model = SshFp
        exclude = ("machine",)

    def __init__(self, *args, **kwargs):
        prefix = kwargs.pop("prefix", self.Meta.model.__name__)
        super(SshFpForm, self).__init__(*args, prefix=prefix, **kwargs)
