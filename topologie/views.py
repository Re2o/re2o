# Re2o est un logiciel d'administration développé initiallement au rezometz. Il
# se veut agnostique au réseau considéré, de manière à être installable en
# quelques clics.
#
# Copyright © 2017  Gabriel Détraz
# Copyright © 2017  Lara Kermarec
# Copyright © 2017  Augustin Lemesle
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
Views for the 'topologie' app of re2o.

They are used to create, edit and delete:
    * a port (add_port, edit_port, del_port)
    * a switch: the views call forms for switches but also machines (domain,
    interface and machine), send and save them at the same time.
    TODO rationalise, enforce the creation of machines (interfaces, domains
    etc.) in models and forms from 'topologie'
    * a room (new_room, edit_room, del_room)
    * a stack
    * histories of all objects mentioned.
"""
from __future__ import unicode_literals

from django.urls import reverse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.db.models import ProtectedError, Prefetch
from django.core.exceptions import ValidationError
from django.template import Context, Template, loader
from django.utils.translation import ugettext as _

import tempfile

from users.views import form
from re2o.base import re2o_paginator, SortTable
from re2o.acl import can_create, can_edit, can_delete, can_view, can_view_all
from re2o.settings import MEDIA_ROOT
from machines.forms import (
    DomainForm,
    EditInterfaceForm,
    AddInterfaceForm,
    EditOptionVlanForm,
)
from machines.views import generate_ipv4_mbf_param
from machines.models import Interface, Service_link, Vlan
from preferences.models import AssoOption, GeneralOption

from .models import (
    Switch,
    Port,
    Room,
    Stack,
    ModelSwitch,
    ConstructorSwitch,
    AccessPoint,
    SwitchBay,
    Building,
    Dormitory,
    Server,
    PortProfile,
    ModuleSwitch,
    ModuleOnSwitch,
)
from .forms import (
    EditPortForm,
    NewSwitchForm,
    EditSwitchForm,
    AddPortForm,
    EditRoomForm,
    StackForm,
    EditModelSwitchForm,
    EditConstructorSwitchForm,
    CreatePortsForm,
    AddAccessPointForm,
    EditAccessPointForm,
    EditSwitchBayForm,
    EditBuildingForm,
    EditDormitoryForm,
    EditPortProfileForm,
    EditModuleForm,
    EditSwitchModuleForm,
)

from subprocess import Popen, PIPE

from os.path import isfile


@login_required
@can_view_all(Switch)
def index(request):
    """View used to display all switches."""
    switch_list = (
        Switch.objects.prefetch_related(
            Prefetch(
                "interface_set",
                queryset=(
                    Interface.objects.select_related(
                        "ipv4__ip_type__extension"
                    ).select_related("domain__extension")
                ),
            )
        )
        .select_related("stack")
        .select_related("switchbay__building__dormitory")
        .select_related("model__constructor")
    )
    switch_list = SortTable.sort(
        switch_list,
        request.GET.get("col"),
        request.GET.get("order"),
        SortTable.TOPOLOGIE_INDEX,
    )

    pagination_number = GeneralOption.get_cached_value("pagination_number")
    switch_list = re2o_paginator(request, switch_list, pagination_number)

    if any(
        service_link.need_regen
        for service_link in Service_link.objects.filter(
            service__service_type="graph_topo"
        )
    ):
        make_machine_graph()
        for service_link in Service_link.objects.filter(
            service__service_type="graph_topo"
        ):
            service_link.done_regen()

    if not isfile("/var/www/re2o/media/images/switchs.png"):
        make_machine_graph()
    return render(request, "topologie/index.html", {"switch_list": switch_list})


@login_required
@can_view_all(PortProfile)
def index_port_profile(request):
    pagination_number = GeneralOption.get_cached_value("pagination_number")
    port_profile_list = (
        PortProfile.objects.all()
        .select_related("vlan_untagged")
        .select_related("on_dormitory")
        .prefetch_related("vlan_tagged")
    )
    port_profile_list = re2o_paginator(request, port_profile_list, pagination_number)
    vlan_list = Vlan.objects.all().order_by("vlan_id")
    return render(
        request,
        "topologie/index_portprofile.html",
        {"port_profile_list": port_profile_list, "vlan_list": vlan_list},
    )


@login_required
@can_view_all(Port)
@can_view(Switch)
def index_port(request, switch, switchid):
    """View used to display all ports related to the given switch."""
    port_list = (
        Port.objects.filter(switch=switch)
        .select_related("room__building__dormitory")
        .select_related("machine_interface__domain__extension")
        .select_related("machine_interface__machine__user")
        .select_related("machine_interface__machine__accesspoint")
        .select_related("related__switch__switchbay__building__dormitory")
        .prefetch_related(
            Prefetch(
                "related__switch__interface_set",
                queryset=(Interface.objects.select_related("domain__extension")),
            )
        )
        .select_related("switch__switchbay__building__dormitory")
        .select_related("switch__model__constructor")
    )
    port_list = SortTable.sort(
        port_list,
        request.GET.get("col"),
        request.GET.get("order"),
        SortTable.TOPOLOGIE_INDEX_PORT,
    )
    return render(
        request,
        "topologie/index_p.html",
        {"port_list": port_list, "id_switch": switchid, "switch": switch},
    )


@login_required
@can_view_all(Room)
def index_room(request):
    """View used to display all rooms."""
    room_list = Room.objects.select_related("building__dormitory")
    room_list = SortTable.sort(
        room_list,
        request.GET.get("col"),
        request.GET.get("order"),
        SortTable.TOPOLOGIE_INDEX_ROOM,
    )
    pagination_number = GeneralOption.get_cached_value("pagination_number")
    room_list = re2o_paginator(request, room_list, pagination_number)
    return render(request, "topologie/index_room.html", {"room_list": room_list})


@login_required
@can_view_all(AccessPoint)
def index_ap(request):
    """View used to display all APs."""
    ap_list = AccessPoint.objects.prefetch_related(
        Prefetch(
            "interface_set",
            queryset=(
                Interface.objects.select_related(
                    "ipv4__ip_type__extension"
                ).select_related("domain__extension")
            ),
        )
    ).distinct()
    ap_list = SortTable.sort(
        ap_list,
        request.GET.get("col"),
        request.GET.get("order"),
        SortTable.TOPOLOGIE_INDEX_BORNE,
    )
    pagination_number = GeneralOption.get_cached_value("pagination_number")
    ap_list = re2o_paginator(request, ap_list, pagination_number)
    return render(request, "topologie/index_ap.html", {"ap_list": ap_list})


@login_required
@can_view_all(Stack, Building, Dormitory, SwitchBay)
def index_physical_grouping(request):
    """View used to display the list of stacks (display all switches)."""
    stack_list = Stack.objects.prefetch_related(
        "switch_set__interface_set__domain__extension"
    )
    building_list = Building.objects.all().select_related("dormitory")
    dormitory_list = Dormitory.objects.all().prefetch_related("building_set")
    switch_bay_list = SwitchBay.objects.select_related(
        "building__dormitory"
    ).prefetch_related("switch_set__interface_set__domain")
    stack_list = SortTable.sort(
        stack_list,
        request.GET.get("col"),
        request.GET.get("order"),
        SortTable.TOPOLOGIE_INDEX_STACK,
    )
    building_list = SortTable.sort(
        building_list,
        request.GET.get("col"),
        request.GET.get("order"),
        SortTable.TOPOLOGIE_INDEX_BUILDING,
    )
    dormitory_list = SortTable.sort(
        dormitory_list,
        request.GET.get("col"),
        request.GET.get("order"),
        SortTable.TOPOLOGIE_INDEX_DORMITORY,
    )
    switch_bay_list = SortTable.sort(
        switch_bay_list,
        request.GET.get("col"),
        request.GET.get("order"),
        SortTable.TOPOLOGIE_INDEX_SWITCH_BAY,
    )
    return render(
        request,
        "topologie/index_physical_grouping.html",
        {
            "stack_list": stack_list,
            "switch_bay_list": switch_bay_list,
            "building_list": building_list,
            "dormitory_list": dormitory_list,
        },
    )


@login_required
@can_view_all(ModelSwitch, ConstructorSwitch)
def index_model_switch(request):
    """View used to display all switch models."""
    model_switch_list = ModelSwitch.objects.select_related(
        "constructor"
    ).prefetch_related("switch_set__interface_set__domain")
    constructor_switch_list = ConstructorSwitch.objects
    model_switch_list = SortTable.sort(
        model_switch_list,
        request.GET.get("col"),
        request.GET.get("order"),
        SortTable.TOPOLOGIE_INDEX_MODEL_SWITCH,
    )
    constructor_switch_list = SortTable.sort(
        constructor_switch_list,
        request.GET.get("col"),
        request.GET.get("order"),
        SortTable.TOPOLOGIE_INDEX_CONSTRUCTOR_SWITCH,
    )
    return render(
        request,
        "topologie/index_model_switch.html",
        {
            "model_switch_list": model_switch_list,
            "constructor_switch_list": constructor_switch_list,
        },
    )


@login_required
@can_view_all(ModuleSwitch)
def index_module(request):
    """View used to display all switch modules."""
    module_list = ModuleSwitch.objects.all()
    modular_switchs = (
        Switch.objects.filter(model__is_modular=True)
        .select_related("model")
        .prefetch_related("moduleonswitch_set__module")
    )
    pagination_number = GeneralOption.get_cached_value("pagination_number")
    module_list = re2o_paginator(request, module_list, pagination_number)
    return render(
        request,
        "topologie/index_module.html",
        {"module_list": module_list, "modular_switchs": modular_switchs},
    )


@login_required
@can_edit(Vlan)
def edit_vlanoptions(request, vlan_instance, **_kwargs):
    """View used to edit options for switch of VLAN object."""
    vlan = EditOptionVlanForm(request.POST or None, instance=vlan_instance)
    if vlan.is_valid():
        if vlan.changed_data:
            vlan.save()
            messages.success(request, _("The VLAN was edited."))
        return redirect(reverse("topologie:index-port-profile"))
    return form(
        {"vlanform": vlan, "action_name": _("Edit")}, "machines/machine.html", request
    )


@login_required
@can_create(Port)
def new_port(request, switchid):
    """View used to create ports."""
    try:
        switch = Switch.objects.get(pk=switchid)
    except Switch.DoesNotExist:
        messages.error(request, _("Nonexistent switch."))
        return redirect(reverse("topologie:index"))
    port = AddPortForm(request.POST or None)
    if port.is_valid():
        port = port.save(commit=False)
        port.switch = switch
        try:
            port.save()
            messages.success(request, _("The port was added."))
        except IntegrityError:
            messages.error(request, _("The port already exists."))
        return redirect(reverse("topologie:index-port", kwargs={"switchid": switchid}))
    return form(
        {"id_switch": switchid, "topoform": port, "action_name": _("Add")},
        "topologie/topo.html",
        request,
    )


@login_required
@can_edit(Port)
def edit_port(request, port_object, **_kwargs):
    """View used to edit ports.

    It enables to change the related switch and the port assignment.
    """
    port = EditPortForm(request.POST or None, instance=port_object)
    if port.is_valid():
        if port.changed_data:
            port.save()
            messages.success(request, _("The port was edited."))
        return redirect(
            reverse(
                "topologie:index-port", kwargs={"switchid": str(port_object.switch.id)}
            )
        )
    return form(
        {
            "id_switch": str(port_object.switch.id),
            "topoform": port,
            "action_name": _("Edit"),
        },
        "topologie/topo.html",
        request,
    )


@login_required
@can_delete(Port)
def del_port(request, port, **_kwargs):
    """View used to delete ports."""
    if request.method == "POST":
        try:
            port.delete()
            messages.success(request, _("The port was deleted."))
        except ProtectedError:
            messages.error(
                request,
                (
                    _(
                        "The port %s is used by another object, impossible to"
                        " delete it."
                    )
                    % port
                ),
            )
        return redirect(
            reverse("topologie:index-port", kwargs={"switchid": str(port.switch.id)})
        )
    return form({"objet": port}, "topologie/delete.html", request)


@login_required
@can_create(Stack)
def new_stack(request):
    """View used to create stacks."""
    stack = StackForm(request.POST or None)
    if stack.is_valid():
        stack.save()
        messages.success(request, _("The stack was created."))
        return redirect(reverse("topologie:index-physical-grouping"))
    return form(
        {"topoform": stack, "action_name": _("Add")}, "topologie/topo.html", request
    )


@login_required
@can_edit(Stack)
def edit_stack(request, stack, **_kwargs):
    """View used to edit stacks."""
    stack = StackForm(request.POST or None, instance=stack)
    if stack.is_valid():
        if stack.changed_data:
            stack.save()
            messages.success(request, _("The stack was edited."))
        return redirect(reverse("topologie:index-physical-grouping"))
    return form(
        {"topoform": stack, "action_name": _("Edit")}, "topologie/topo.html", request
    )


@login_required
@can_delete(Stack)
def del_stack(request, stack, **_kwargs):
    """View used to delete stacks."""
    if request.method == "POST":
        try:
            stack.delete()
            messages.success(request, _("The stack was deleted."))
        except ProtectedError:
            messages.error(
                request,
                (
                    _(
                        "The stack %s is used by another object, impossible to"
                        " deleted it."
                    )
                    % stack
                ),
            )
        return redirect(reverse("topologie:index-physical-grouping"))
    return form({"objet": stack}, "topologie/delete.html", request)


@login_required
@can_edit(Stack)
def edit_switchs_stack(request, stack, **_kwargs):
    """View used to edit the list of switches of the given stack."""
    if request.method == "POST":
        pass
    else:
        context = {"stack": stack}
        context["switchs_stack"] = stack.switchs_set.all()
        context["switchs_autres"] = Switch.object.filter(stack=None)


@login_required
@can_create(Switch)
def new_switch(request):
    """View used to create switches.

    At the same time, it creates the related interface and machine. The view
    successively calls the 4 appropriate forms: machine, interface, domain and
    switch.
    """
    switch = NewSwitchForm(request.POST or None, user=request.user)
    interface = AddInterfaceForm(request.POST or None, user=request.user)
    domain = DomainForm(request.POST or None, user=request.user)
    if switch.is_valid() and interface.is_valid():
        user = AssoOption.get_cached_value("utilisateur_asso")
        if not user:
            messages.error(
                request,
                (
                    _(
                        "The organisation's user doesn't exist yet, please create"
                        " or link it in the preferences."
                    )
                ),
            )
            return redirect(reverse("topologie:index"))
        new_switch_obj = switch.save(commit=False)
        new_switch_obj.user = user
        new_interface_obj = interface.save(commit=False)
        domain.instance.interface_parent = new_interface_obj
        if domain.is_valid():
            new_domain_obj = domain.save(commit=False)
            new_switch_obj.save()
            new_interface_obj.machine = new_switch_obj
            new_interface_obj.save()
            new_domain_obj.interface_parent = new_interface_obj
            new_domain_obj.save()
            messages.success(request, _("The switch was created."))
            return redirect(reverse("topologie:index"))
    i_mbf_param = generate_ipv4_mbf_param(interface, False)
    return form(
        {
            "topoform": interface,
            "machineform": switch,
            "domainform": domain,
            "i_mbf_param": i_mbf_param,
            "device": _("switch"),
        },
        "topologie/topo_more.html",
        request,
    )


@login_required
@can_create(Port)
def create_ports(request, switchid):
    """View used to create port lists for the given switch."""
    try:
        switch = Switch.objects.get(pk=switchid)
    except Switch.DoesNotExist:
        messages.error(request, _("Nonexistent switch."))
        return redirect(reverse("topologie:index"))

    first_port = getattr(switch.ports.order_by("port").first(), "port", 1)
    last_port = switch.number + first_port - 1
    port_form = CreatePortsForm(
        request.POST or None, initial={"begin": first_port, "end": last_port}
    )
    if port_form.is_valid():
        begin = port_form.cleaned_data["begin"]
        end = port_form.cleaned_data["end"]
        try:
            switch.create_ports(begin, end)
            messages.success(request, _("The ports were created."))
        except ValidationError as e:
            messages.error(request, "".join(e))
        return redirect(reverse("topologie:index-port", kwargs={"switchid": switchid}))
    return form(
        {"id_switch": switchid, "topoform": port_form}, "topologie/switch.html", request
    )


@login_required
@can_edit(Switch)
def edit_switch(request, switch, switchid):
    """View used to edit switches.

    It enables to change the number of ports, location in the stack, or the
    related interface and machine.
    """
    switch_form = EditSwitchForm(
        request.POST or None, instance=switch, user=request.user
    )
    interface_form = EditInterfaceForm(
        request.POST or None, instance=switch.interface_set.first(), user=request.user
    )
    domain_form = DomainForm(
        request.POST or None,
        instance=switch.interface_set.first().domain,
        user=request.user,
    )
    if switch_form.is_valid() and interface_form.is_valid():
        new_switch_obj = switch_form.save(commit=False)
        new_interface_obj = interface_form.save(commit=False)
        new_domain_obj = domain_form.save(commit=False)
        if switch_form.changed_data:
            new_switch_obj.save()
        if interface_form.changed_data:
            new_interface_obj.save()
        if domain_form.changed_data:
            new_domain_obj.save()
        messages.success(request, _("The switch was edited."))
        return redirect(reverse("topologie:index"))
    i_mbf_param = generate_ipv4_mbf_param(interface_form, False)
    return form(
        {
            "id_switch": switchid,
            "topoform": interface_form,
            "machineform": switch_form,
            "domainform": domain_form,
            "i_mbf_param": i_mbf_param,
            "device": _("switch"),
        },
        "topologie/topo_more.html",
        request,
    )


@login_required
@can_create(AccessPoint)
def new_ap(request):
    """View used to create APs.

    At the same time, it creates the related interface and machine. The view
    successively calls the 3 appropriate forms: machine, interface, domain.
    """
    ap = AddAccessPointForm(request.POST or None, user=request.user)
    interface = AddInterfaceForm(request.POST or None, user=request.user)
    domain = DomainForm(request.POST or None, user=request.user)
    if ap.is_valid() and interface.is_valid():
        user = AssoOption.get_cached_value("utilisateur_asso")
        if not user:
            messages.error(
                request,
                (
                    _(
                        "The organisation's user doesn't exist yet, please create"
                        " or link it in the preferences."
                    )
                ),
            )
            return redirect(reverse("topologie:index"))
        new_ap_obj = ap.save(commit=False)
        new_ap_obj.user = user
        new_interface_obj = interface.save(commit=False)
        domain.instance.interface_parent = new_interface_obj
        if domain.is_valid():
            new_domain_obj = domain.save(commit=False)
            new_ap_obj.save()
            new_interface_obj.machine = new_ap_obj
            new_interface_obj.save()
            new_domain_obj.interface_parent = new_interface_obj
            new_domain_obj.save()
            messages.success(request, _("The access point was created."))
            return redirect(reverse("topologie:index-ap"))
    i_mbf_param = generate_ipv4_mbf_param(interface, False)
    return form(
        {
            "topoform": interface,
            "machineform": ap,
            "domainform": domain,
            "i_mbf_param": i_mbf_param,
            "device": _("access point"),
        },
        "topologie/topo_more.html",
        request,
    )


@login_required
@can_edit(AccessPoint)
def edit_ap(request, ap, **_kwargs):
    """View used to edit APs."""
    interface_form = EditInterfaceForm(
        request.POST or None, user=request.user, instance=ap.interface_set.first()
    )
    ap_form = EditAccessPointForm(request.POST or None, user=request.user, instance=ap)
    domain_form = DomainForm(
        request.POST or None,
        instance=ap.interface_set.first().domain,
        user=request.user,
    )
    if ap_form.is_valid() and interface_form.is_valid():
        user = AssoOption.get_cached_value("utilisateur_asso")
        if not user:
            messages.error(
                request,
                (
                    _(
                        "The organisation's user doesn't exist yet, please create"
                        " or link it in the preferences."
                    )
                ),
            )
            return redirect(reverse("topologie:index-ap"))
        new_ap_obj = ap_form.save(commit=False)
        new_interface_obj = interface_form.save(commit=False)
        new_domain_obj = domain_form.save(commit=False)
        if ap_form.changed_data:
            new_ap_obj.save()
        if interface_form.changed_data:
            new_interface_obj.save()
        if domain_form.changed_data:
            new_domain_obj.save()
        messages.success(request, _("The access point was edited."))
        return redirect(reverse("topologie:index-ap"))
    i_mbf_param = generate_ipv4_mbf_param(interface_form, False)
    return form(
        {
            "topoform": interface_form,
            "machineform": ap_form,
            "domainform": domain_form,
            "i_mbf_param": i_mbf_param,
            "device": _("access point"),
        },
        "topologie/topo_more.html",
        request,
    )


@login_required
@can_create(Room)
def new_room(request):
    """View used to create rooms."""
    room = EditRoomForm(request.POST or None)
    if room.is_valid():
        room.save()
        messages.success(request, _("The room was created."))
        return redirect(reverse("topologie:index-room"))
    return form(
        {"topoform": room, "action_name": _("Add")}, "topologie/topo.html", request
    )


@login_required
@can_edit(Room)
def edit_room(request, room, **_kwargs):
    """View used to edit rooms."""
    room = EditRoomForm(request.POST or None, instance=room)
    if room.is_valid():
        if room.changed_data:
            room.save()
            messages.success(request, _("The room was edited."))
        return redirect(reverse("topologie:index-room"))
    return form(
        {"topoform": room, "action_name": _("Edit")}, "topologie/topo.html", request
    )


@login_required
@can_delete(Room)
def del_room(request, room, **_kwargs):
    """View used to delete rooms."""
    if request.method == "POST":
        try:
            room.delete()
            messages.success(request, _("The room was deleted."))
        except ProtectedError:
            messages.error(
                request,
                (
                    _(
                        "The room %s is used by another object, impossible to"
                        " deleted it."
                    )
                    % room
                ),
            )
        return redirect(reverse("topologie:index-room"))
    return form(
        {"objet": room, "objet_name": _("room")}, "topologie/delete.html", request
    )


@login_required
@can_create(ModelSwitch)
def new_model_switch(request):
    """View used to create switch models."""
    model_switch = EditModelSwitchForm(request.POST or None)
    if model_switch.is_valid():
        model_switch.save()
        messages.success(request, _("The switch model was created."))
        return redirect(reverse("topologie:index-model-switch"))
    return form(
        {"topoform": model_switch, "action_name": _("Add")},
        "topologie/topo.html",
        request,
    )


@login_required
@can_edit(ModelSwitch)
def edit_model_switch(request, model_switch, **_kwargs):
    """View used to edit switch models."""
    model_switch = EditModelSwitchForm(request.POST or None, instance=model_switch)
    if model_switch.is_valid():
        if model_switch.changed_data:
            model_switch.save()
            messages.success(request, _("The switch model was edited."))
        return redirect(reverse("topologie:index-model-switch"))
    return form(
        {"topoform": model_switch, "action_name": _("Edit")},
        "topologie/topo.html",
        request,
    )


@login_required
@can_delete(ModelSwitch)
def del_model_switch(request, model_switch, **_kwargs):
    """View used to delete switch models."""
    if request.method == "POST":
        try:
            model_switch.delete()
            messages.success(request, _("The switch model was deleted."))
        except ProtectedError:
            messages.error(
                request,
                (
                    _(
                        "The switch model %s is used by another object,"
                        " impossible to delete it."
                    )
                    % model_switch
                ),
            )
        return redirect(reverse("topologie:index-model-switch"))
    return form(
        {"objet": model_switch, "objet_name": _("switch model")},
        "topologie/delete.html",
        request,
    )


@login_required
@can_create(SwitchBay)
def new_switch_bay(request):
    """View used to create switch bays."""
    switch_bay = EditSwitchBayForm(request.POST or None)
    if switch_bay.is_valid():
        switch_bay.save()
        messages.success(request, _("The switch bay was created."))
        return redirect(reverse("topologie:index-physical-grouping"))
    return form(
        {"topoform": switch_bay, "action_name": _("Add")},
        "topologie/topo.html",
        request,
    )


@login_required
@can_edit(SwitchBay)
def edit_switch_bay(request, switch_bay, **_kwargs):
    """View used to edit switch bays."""
    switch_bay = EditSwitchBayForm(request.POST or None, instance=switch_bay)
    if switch_bay.is_valid():
        if switch_bay.changed_data:
            switch_bay.save()
            messages.success(request, _("The switch bay was edited."))
        return redirect(reverse("topologie:index-physical-grouping"))
    return form(
        {"topoform": switch_bay, "action_name": _("Edit")},
        "topologie/topo.html",
        request,
    )


@login_required
@can_delete(SwitchBay)
def del_switch_bay(request, switch_bay, **_kwargs):
    """View used to delete switch bays."""
    if request.method == "POST":
        try:
            switch_bay.delete()
            messages.success(request, _("The switch bay was deleted."))
        except ProtectedError:
            messages.error(
                request,
                (
                    _(
                        "The switch bay %s is used by another object,"
                        " impossible to delete it."
                    )
                    % switch_bay
                ),
            )
        return redirect(reverse("topologie:index-physical-grouping"))
    return form(
        {"objet": switch_bay, "objet_name": _("switch bay")},
        "topologie/delete.html",
        request,
    )


@login_required
@can_create(Building)
def new_building(request):
    """View used to create buildings."""
    building = EditBuildingForm(request.POST or None)
    if building.is_valid():
        building.save()
        messages.success(request, _("The building was created."))
        return redirect(reverse("topologie:index-physical-grouping"))
    return form(
        {"topoform": building, "action_name": _("Add")},
        "topologie/topo.html",
        request,
    )


@login_required
@can_edit(Building)
def edit_building(request, building, **_kwargs):
    """View used to edit buildings."""
    building = EditBuildingForm(request.POST or None, instance=building)
    if building.is_valid():
        if building.changed_data:
            building.save()
            messages.success(request, _("The building was edited."))
        return redirect(reverse("topologie:index-physical-grouping"))
    return form(
        {"topoform": building, "action_name": _("Edit")}, "topologie/topo.html", request
    )


@login_required
@can_delete(Building)
def del_building(request, building, **_kwargs):
    """View used to delete buildings."""
    if request.method == "POST":
        try:
            building.delete()
            messages.success(request, _("The building was deleted."))
        except ProtectedError:
            messages.error(
                request,
                (
                    _(
                        "The building %s is used by another object, impossible"
                        " to delete it."
                    )
                    % building
                ),
            )
        return redirect(reverse("topologie:index-physical-grouping"))
    return form(
        {"objet": building, "objet_name": _("building")},
        "topologie/delete.html",
        request,
    )


@login_required
@can_create(Dormitory)
def new_dormitory(request):
    """View used to create dormitories."""
    dormitory = EditDormitoryForm(request.POST or None)
    if dormitory.is_valid():
        dormitory.save()
        messages.success(request, _("The dormitory was created."))
        return redirect(reverse("topologie:index-physical-grouping"))
    return form(
        {"topoform": dormitory, "action_name": _("Add")},
        "topologie/topo.html",
        request,
    )


@login_required
@can_edit(Dormitory)
def edit_dormitory(request, dormitory, **_kwargs):
    """View used to edit dormitories."""
    dormitory = EditDormitoryForm(request.POST or None, instance=dormitory)
    if dormitory.is_valid():
        if dormitory.changed_data:
            dormitory.save()
            messages.success(request, _("The dormitory was edited."))
        return redirect(reverse("topologie:index-physical-grouping"))
    return form(
        {"topoform": dormitory, "action_name": _("Edit")},
        "topologie/topo.html",
        request,
    )


@login_required
@can_delete(Dormitory)
def del_dormitory(request, dormitory, **_kwargs):
    """View used to delete dormitories."""
    if request.method == "POST":
        try:
            dormitory.delete()
            messages.success(request, _("The dormitory was deleted."))
        except ProtectedError:
            messages.error(
                request,
                (
                    _(
                        "The dormitory %s is used by another object, impossible"
                        " to delete it."
                    )
                    % dormitory
                ),
            )
        return redirect(reverse("topologie:index-physical-grouping"))
    return form(
        {"objet": dormitory, "objet_name": _("dormitory")},
        "topologie/delete.html",
        request,
    )


@login_required
@can_create(ConstructorSwitch)
def new_constructor_switch(request):
    """View used to create switch constructors."""
    constructor_switch = EditConstructorSwitchForm(request.POST or None)
    if constructor_switch.is_valid():
        constructor_switch.save()
        messages.success(request, _("The switch constructor was created."))
        return redirect(reverse("topologie:index-model-switch"))
    return form(
        {"topoform": constructor_switch, "action_name": _("Add")},
        "topologie/topo.html",
        request,
    )


@login_required
@can_edit(ConstructorSwitch)
def edit_constructor_switch(request, constructor_switch, **_kwargs):
    """View used to edit switch constructors."""
    constructor_switch = EditConstructorSwitchForm(
        request.POST or None, instance=constructor_switch
    )
    if constructor_switch.is_valid():
        if constructor_switch.changed_data:
            constructor_switch.save()
            messages.success(request, _("The switch constructor was edited."))
        return redirect(reverse("topologie:index-model-switch"))
    return form(
        {"topoform": constructor_switch, "action_name": _("Edit")},
        "topologie/topo.html",
        request,
    )


@login_required
@can_delete(ConstructorSwitch)
def del_constructor_switch(request, constructor_switch, **_kwargs):
    """View used to delete switch constructors."""
    if request.method == "POST":
        try:
            constructor_switch.delete()
            messages.success(request, _("The switch constructor was deleted."))
        except ProtectedError:
            messages.error(
                request,
                (
                    _(
                        "The switch constructor %s is used by another object,"
                        " impossible to delete it."
                    )
                    % constructor_switch
                ),
            )
        return redirect(reverse("topologie:index-model-switch"))
    return form(
        {"objet": constructor_switch, "objet_name": _("switch constructor")},
        "topologie/delete.html",
        request,
    )


@login_required
@can_create(PortProfile)
def new_port_profile(request):
    """View used to create port profiles."""
    port_profile = EditPortProfileForm(request.POST or None)
    if port_profile.is_valid():
        port_profile.save()
        messages.success(request, _("The port profile was created."))
        return redirect(reverse("topologie:index-port-profile"))
    return form(
        {"topoform": port_profile, "action_name": _("Add")},
        "topologie/topo.html",
        request,
    )


@login_required
@can_edit(PortProfile)
def edit_port_profile(request, port_profile, **_kwargs):
    """View used to edit port profiles."""
    port_profile = EditPortProfileForm(request.POST or None, instance=port_profile)
    if port_profile.is_valid():
        if port_profile.changed_data:
            port_profile.save()
            messages.success(request, _("The port profile was edited."))
        return redirect(reverse("topologie:index-port-profile"))
    return form(
        {"topoform": port_profile, "action_name": _("Edit")},
        "topologie/topo.html",
        request,
    )


@login_required
@can_delete(PortProfile)
def del_port_profile(request, port_profile, **_kwargs):
    """View used to delete port profiles."""
    if request.method == "POST":
        try:
            port_profile.delete()
            messages.success(request, _("The port profile was deleted."))
        except ProtectedError:
            messages.success(request, _("Impossible to delete the port profile."))
        return redirect(reverse("topologie:index-port-profile"))
    return form(
        {"objet": port_profile, "objet_name": _("port profile")},
        "topologie/delete.html",
        request,
    )


@login_required
@can_create(ModuleSwitch)
def add_module(request):
    """View used to create switch modules."""
    module = EditModuleForm(request.POST or None)
    if module.is_valid():
        module.save()
        messages.success(request, _("The module was created."))
        return redirect(reverse("topologie:index-module"))
    return form(
        {"topoform": module, "action_name": _("Add")}, "topologie/topo.html", request
    )


@login_required
@can_edit(ModuleSwitch)
def edit_module(request, module_instance, **_kwargs):
    """View used to edit switch modules."""
    module = EditModuleForm(request.POST or None, instance=module_instance)
    if module.is_valid():
        if module.changed_data:
            module.save()
            messages.success(request, _("The module was edited."))
        return redirect(reverse("topologie:index-module"))
    return form(
        {"topoform": module, "action_name": _("Edit")}, "topologie/topo.html", request
    )


@login_required
@can_delete(ModuleSwitch)
def del_module(request, module, **_kwargs):
    """View used to delete switch modules."""
    if request.method == "POST":
        try:
            module.delete()
            messages.success(request, _("The module was deleted."))
        except ProtectedError:
            messages.error(
                request,
                (
                    _(
                        "The module %s is used by another object, impossible to"
                        " deleted it."
                    )
                    % module
                ),
            )
        return redirect(reverse("topologie:index-module"))
    return form(
        {"objet": module, "objet_name": _("module")}, "topologie/delete.html", request
    )


@login_required
@can_create(ModuleOnSwitch)
def add_module_on(request):
    """View used to add a module to a switch."""
    module_switch = EditSwitchModuleForm(request.POST or None)
    if module_switch.is_valid():
        module_switch.save()
        messages.success(request, _("The module was added."))
        return redirect(reverse("topologie:index-module"))
    return form(
        {"topoform": module_switch, "action_name": _("Add")},
        "topologie/topo.html",
        request,
    )


@login_required
@can_edit(ModuleOnSwitch)
def edit_module_on(request, module_instance, **_kwargs):
    """View used to edit a module on a switch."""
    module = EditSwitchModuleForm(request.POST or None, instance=module_instance)
    if module.is_valid():
        if module.changed_data:
            module.save()
            messages.success(request, _("The module was edited."))
        return redirect(reverse("topologie:index-module"))
    return form(
        {"topoform": module, "action_name": _("Edit")}, "topologie/topo.html", request
    )


@login_required
@can_delete(ModuleOnSwitch)
def del_module_on(request, module, **_kwargs):
    """View used to delete a module on a switch."""
    if request.method == "POST":
        try:
            module.delete()
            messages.success(request, _("The module was deleted."))
        except ProtectedError:
            messages.error(
                request,
                (
                    _(
                        "The module %s is used by another object, impossible to"
                        " deleted it."
                    )
                    % module
                ),
            )
        return redirect(reverse("topologie:index-module"))
    return form(
        {"objet": module, "objet_name": _("module")}, "topologie/delete.html", request
    )


def make_machine_graph():
    """Create the graph of switches, machines and access points."""
    dico = {
        "subs": [],
        "links": [],
        "alone": [],
        "colors": {
            "head": "#7f0505",  # Color parameters for the graph
            "back": "#b5adad",
            "texte": "#563d01",
            "border_bornes": "#02078e",
            "head_bornes": "#25771c",
            "head_server": "#1c3777",
        },
    }
    missing = list(
        Switch.objects.prefetch_related(
            Prefetch(
                "interface_set",
                queryset=(
                    Interface.objects.select_related(
                        "ipv4__ip_type__extension"
                    ).select_related("domain__extension")
                ),
            )
        )
    )
    detected = []
    for building in Building.objects.all():  # Visit all buildings

        dico["subs"].append(
            {
                "bat_id": building.id,
                "bat_name": building,
                "switchs": [],
                "bornes": [],
                "machines": [],
            }
        )
        # Visit all switches in this building
        for switch in (
            Switch.objects.filter(switchbay__building=building)
            .prefetch_related(
                Prefetch(
                    "interface_set",
                    queryset=(
                        Interface.objects.select_related(
                            "ipv4__ip_type__extension"
                        ).select_related("domain__extension")
                    ),
                )
            )
            .select_related("switchbay__building")
            .select_related("switchbay__building__dormitory")
            .select_related("model__constructor")
        ):
            dico["subs"][-1]["switchs"].append(
                {
                    "name": switch.get_name,
                    "nombre": switch.number,
                    "model": switch.model,
                    "id": switch.id,
                    "batiment": building,
                    "ports": [],
                }
            )
            # visit all ports of this switch and add the switches linked to it
            for port in switch.ports.filter(related__isnull=False).select_related(
                "related__switch"
            ):
                dico["subs"][-1]["switchs"][-1]["ports"].append(
                    {"numero": port.port, "related": port.related.switch.get_name}
                )

        for ap in AccessPoint.all_ap_in(building).prefetch_related(
            Prefetch(
                "interface_set",
                queryset=(
                    Interface.objects.select_related(
                        "ipv4__ip_type__extension"
                    ).select_related("domain__extension")
                ),
            )
        ):
            switch = ap.switch().first()
            dico["subs"][-1]["bornes"].append(
                {
                    "name": ap.short_name,
                    "switch": switch.get_name,
                    "port": switch.ports.filter(machine_interface__machine=ap)
                    .first()
                    .port,
                }
            )
        for server in Server.all_server_in(building).prefetch_related(
            Prefetch(
                "interface_set",
                queryset=(
                    Interface.objects.select_related(
                        "ipv4__ip_type__extension"
                    ).select_related("domain__extension")
                ),
            )
        ):
            dico["subs"][-1]["machines"].append(
                {
                    "name": server.short_name,
                    "switch": server.switch().first().get_name,
                    "port": Port.objects.filter(machine_interface__machine=server)
                    .first()
                    .port,
                }
            )

    # While the list of forgotten ones is not empty
    while missing:
        if missing[0].ports.count():  # The switch is not empty
            links, new_detected = recursive_switchs(missing[0], None, [missing[0]])
            for link in links:
                dico["links"].append(link)
            # Update the lists of missings and already detected switches
            missing = [i for i in missing if i not in new_detected]
            detected += new_detected
        # If the switch has no ports, don't explore it and hop to the next one
        else:
            del missing[0]
    # Switches that are not connected or not in a building
    for switch in Switch.objects.filter(switchbay__isnull=True).exclude(
        ports__related__isnull=False
    ):
        dico["alone"].append({"id": switch.id, "name": switch.get_name})

    # Generate the dot file
    dot_data = generate_dot(dico, "topologie/graph_switch.dot")

    # Create a temporary file to store the dot data
    f = tempfile.NamedTemporaryFile(mode="w+", encoding="utf-8", delete=False)
    with f:
        f.write(dot_data)
    unflatten = Popen(  # Unflatten the graph to make it look better
        ["unflatten", "-l", "3", f.name], stdout=PIPE
    )
    Popen(  # Pipe the result of the first command into the second
        ["dot", "-Tpng", "-o", MEDIA_ROOT + "/images/switchs.png"],
        stdin=unflatten.stdout,
        stdout=PIPE,
    )


def generate_dot(data, template):
    """Generate a dot file from the data and template given.

    Args:
        data: dictionary passed to the template.
        template: path to the dot template.

    Returns:
        All the lines of the dot file.
    """
    t = loader.get_template(template)
    if not isinstance(t, Template) and not (
        hasattr(t, "template") and isinstance(t.template, Template)
    ):
        raise Exception(
            _(
                "The default Django template isn't used. This can"
                " lead to rendering errors. Check the parameters."
            )
        )
    c = Context(data).flatten()
    dot = t.render(c)
    return dot


def recursive_switchs(switch_start, switch_before, detected):
    """Visit the switch and travel to the switches linked to it.

    Args:
        switch_start: the switch to begin the visit on.
        switch_before: the switch that you come from. None if switch_start is the first one.
        detected: list of all switches already visited. None if switch_start is the first one.

    Returns:
        A list of all the links found and a list of all the switches visited.
    """
    detected.append(switch_start)
    links_return = []  # List of dictionaries of the links to be detected
    # Create links to every switches below
    for port in switch_start.ports.filter(related__isnull=False):
        # Not the switch that we come from, not the current switch
        if (
            port.related.switch != switch_before
            and port.related.switch != port.switch
            and port.related.switch not in detected
        ):
            links = {  # Dictionary of a link
                "depart": switch_start.id,
                "arrive": port.related.switch.id,
            }
            links_return.append(links)  # Add current and below levels links

    # Go down on every related switches
    for port in switch_start.ports.filter(related__isnull=False):
        # The switch at the end of this link has not been visited
        if port.related.switch not in detected:
            # Explore it and get the results
            links_down, detected = recursive_switchs(
                port.related.switch, switch_start, detected
            )
            # Add the non empty links to the current list
            for link in links_down:
                if link:
                    links_return.append(link)
    return (links_return, detected)
