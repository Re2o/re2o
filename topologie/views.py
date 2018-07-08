# Re2o est un logiciel d'administration développé initiallement au rezometz. Il
# se veut agnostique au réseau considéré, de manière à être installable en
# quelques clics.
#
# Copyright © 2017  Gabriel Détraz
# Copyright © 2017  Goulven Kermarec
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
Page des vues de l'application topologie

Permet de créer, modifier et supprimer :
- un port (add_port, edit_port, del_port)
- un switch : les vues d'ajout et d'édition font appel aux forms de creation
de switch, mais aussi aux forms de machines.forms (domain, interface et
machine). Le views les envoie et les save en même temps. TODO : rationaliser
et faire que la creation de machines (interfaces, domain etc) soit gérée
coté models et forms de topologie
- une chambre (new_room, edit_room, del_room)
- une stack
- l'historique de tous les objets cités
"""
from __future__ import unicode_literals

from django.urls import reverse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.db.models import ProtectedError, Prefetch
from django.core.exceptions import ValidationError
from django.contrib.staticfiles.storage import staticfiles_storage
from django.template.loader import get_template
from django.template import Context, Template, loader
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import ugettext as _

import tempfile

from users.views import form
from re2o.utils import re2o_paginator, SortTable
from re2o.acl import (
    can_create,
    can_edit,
    can_delete,
    can_view,
    can_view_all,
)
from re2o.settings import MEDIA_ROOT
from machines.forms import (
    DomainForm,
    EditInterfaceForm,
    AddInterfaceForm,
    EditOptionVlanForm
)
from machines.views import generate_ipv4_mbf_param
from machines.models import (
    Interface,
    Service_link, 
    Vlan
)
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
    Server,
    PortProfile,
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
    EditPortProfileForm,
)

from subprocess import (
    Popen,
    PIPE
)

from os.path import isfile 
from os import remove


@login_required
@can_view_all(Switch)
def index(request):
    """ Vue d'affichage de tous les swicthes"""
    switch_list = (Switch.objects
                   .prefetch_related(Prefetch(
                       'interface_set',
                       queryset=(Interface.objects
                                 .select_related('ipv4__ip_type__extension')
                                 .select_related('domain__extension'))
                   ))
                   .select_related('stack'))
    switch_list = SortTable.sort(
        switch_list,
        request.GET.get('col'),
        request.GET.get('order'),
        SortTable.TOPOLOGIE_INDEX
    )


    pagination_number = GeneralOption.get_cached_value('pagination_number')
    switch_list = re2o_paginator(request, switch_list, pagination_number)

    if any(service_link.need_regen for service_link in Service_link.objects.filter(service__service_type='graph_topo')):
        make_machine_graph()
        for service_link in Service_link.objects.filter(service__service_type='graph_topo'):
            service_link.done_regen()

    if not isfile("/var/www/re2o/media/images/switchs.png"):
        make_machine_graph()
    return render(
        request,
        'topologie/index.html',
        {'switch_list': switch_list}
    )


@login_required
@can_view_all(PortProfile)
def index_port_profile(request):
    pagination_number = GeneralOption.get_cached_value('pagination_number')
    port_profile_list = PortProfile.objects.all().select_related('vlan_untagged')
    port_profile_list = re2o_paginator(request, port_profile_list, pagination_number)
    vlan_list = Vlan.objects.all().order_by('vlan_id')
    return render(
        request,
        'topologie/index_portprofile.html',
        {'port_profile_list': port_profile_list, 'vlan_list': vlan_list}
    )


@login_required
@can_view_all(Port)
@can_view(Switch)
def index_port(request, switch, switchid):
    """ Affichage de l'ensemble des ports reliés à un switch particulier"""
    port_list = (Port.objects
                 .filter(switch=switch)
                 .select_related('room')
                 .select_related('machine_interface__domain__extension')
                 .select_related('machine_interface__machine__user')
                 .select_related('related__switch')
                 .prefetch_related(Prefetch(
                     'related__switch__interface_set',
                     queryset=(Interface.objects
                               .select_related('domain__extension'))
                 ))
                 .select_related('switch'))
    port_list = SortTable.sort(
        port_list,
        request.GET.get('col'),
        request.GET.get('order'),
        SortTable.TOPOLOGIE_INDEX_PORT
    )
    return render(
        request,
        'topologie/index_p.html',
        {
            'port_list': port_list,
            'id_switch': switchid,
            'nom_switch': switch
        }
    )


@login_required
@can_view_all(Room)
def index_room(request):
    """ Affichage de l'ensemble des chambres"""
    room_list = Room.objects
    room_list = SortTable.sort(
        room_list,
        request.GET.get('col'),
        request.GET.get('order'),
        SortTable.TOPOLOGIE_INDEX_ROOM
    )
    pagination_number = GeneralOption.get_cached_value('pagination_number')
    room_list = re2o_paginator(request, room_list, pagination_number)
    return render(
        request,
        'topologie/index_room.html',
        {'room_list': room_list}
    )


@login_required
@can_view_all(AccessPoint)
def index_ap(request):
    """ Affichage de l'ensemble des bornes"""
    ap_list = (AccessPoint.objects
               .prefetch_related(Prefetch(
                   'interface_set',
                   queryset=(Interface.objects
                             .select_related('ipv4__ip_type__extension')
                             .select_related('domain__extension'))
               )))
    ap_list = SortTable.sort(
        ap_list,
        request.GET.get('col'),
        request.GET.get('order'),
        SortTable.TOPOLOGIE_INDEX_BORNE
    )
    pagination_number = GeneralOption.get_cached_value('pagination_number')
    ap_list = re2o_paginator(request, ap_list, pagination_number)
    return render(
        request,
        'topologie/index_ap.html',
        {'ap_list': ap_list}
    )


@login_required
@can_view_all(Stack, Building, SwitchBay)
def index_physical_grouping(request):
    """Affichage de la liste des stacks (affiche l'ensemble des switches)"""
    stack_list = (Stack.objects
                  .prefetch_related(
                      'switch_set__interface_set__domain__extension'
                  ))
    building_list = Building.objects.all()
    switch_bay_list = SwitchBay.objects.select_related('building')
    stack_list = SortTable.sort(
        stack_list,
        request.GET.get('col'),
        request.GET.get('order'),
        SortTable.TOPOLOGIE_INDEX_STACK
    )
    building_list = SortTable.sort(
        building_list,
        request.GET.get('col'),
        request.GET.get('order'),
        SortTable.TOPOLOGIE_INDEX_BUILDING
    )
    switch_bay_list = SortTable.sort(
        switch_bay_list,
        request.GET.get('col'),
        request.GET.get('order'),
        SortTable.TOPOLOGIE_INDEX_SWITCH_BAY
    )
    return render(
        request,
        'topologie/index_physical_grouping.html',
        {
            'stack_list': stack_list,
            'switch_bay_list': switch_bay_list,
            'building_list': building_list,
        }
    )


@login_required
@can_view_all(ModelSwitch, ConstructorSwitch)
def index_model_switch(request):
    """ Affichage de l'ensemble des modèles de switches"""
    model_switch_list = ModelSwitch.objects.select_related('constructor')
    constructor_switch_list = ConstructorSwitch.objects
    model_switch_list = SortTable.sort(
        model_switch_list,
        request.GET.get('col'),
        request.GET.get('order'),
        SortTable.TOPOLOGIE_INDEX_MODEL_SWITCH
    )
    constructor_switch_list = SortTable.sort(
        constructor_switch_list,
        request.GET.get('col'),
        request.GET.get('order'),
        SortTable.TOPOLOGIE_INDEX_CONSTRUCTOR_SWITCH
    )
    return render(
        request,
        'topologie/index_model_switch.html',
        {
            'model_switch_list': model_switch_list,
            'constructor_switch_list': constructor_switch_list,
        }
    )


@login_required
@can_edit(Vlan)
def edit_vlanoptions(request, vlan_instance, **_kwargs):
    """ View used to edit options for switch of VLAN object """
    vlan = EditOptionVlanForm(request.POST or None, instance=vlan_instance)
    if vlan.is_valid():
        if vlan.changed_data:
            vlan.save()
            messages.success(request, "Vlan modifié")
        return redirect(reverse('topologie:index-port-profile'))
    return form(
        {'vlanform': vlan, 'action_name': 'Editer'},
        'machines/machine.html',
        request
    )


@login_required
@can_create(Port)
def new_port(request, switchid):
    """ Nouveau port"""
    try:
        switch = Switch.objects.get(pk=switchid)
    except Switch.DoesNotExist:
        messages.error(request, u"Switch inexistant")
        return redirect(reverse('topologie:index'))
    port = AddPortForm(request.POST or None)
    if port.is_valid():
        port = port.save(commit=False)
        port.switch = switch
        try:
            port.save()
            messages.success(request, "Port ajouté")
        except IntegrityError:
            messages.error(request, "Ce port existe déjà")
        return redirect(reverse(
            'topologie:index-port',
            kwargs={'switchid': switchid}
        ))
    return form(
        {'id_switch': switchid, 'topoform': port, 'action_name': 'Ajouter'},
        'topologie/topo.html',
        request)


@login_required
@can_edit(Port)
def edit_port(request, port_object, **_kwargs):
    """ Edition d'un port. Permet de changer le switch parent et
    l'affectation du port"""

    port = EditPortForm(request.POST or None, instance=port_object)
    if port.is_valid():
        if port.changed_data:
            port.save()
            messages.success(request, "Le port a bien été modifié")
        return redirect(reverse(
            'topologie:index-port',
            kwargs={'switchid': str(port_object.switch.id)}
        ))
    return form(
        {
            'id_switch': str(port_object.switch.id),
            'topoform': port,
            'action_name': 'Editer'
        },
        'topologie/topo.html',
        request
    )


@login_required
@can_delete(Port)
def del_port(request, port, **_kwargs):
    """ Supprime le port"""
    if request.method == "POST":
        try:
            port.delete()
            messages.success(request, "Le port a été détruit")
        except ProtectedError:
            messages.error(
                request,
                ("Le port %s est affecté à un autre objet, impossible "
                 "de le supprimer" % port)
            )
        return redirect(reverse(
            'topologie:index-port',
            kwargs={'switchid': str(port.switch.id)}
        ))
    return form({'objet': port}, 'topologie/delete.html', request)


@login_required
@can_create(Stack)
def new_stack(request):
    """Ajoute un nouveau stack : stackid_min, max, et nombre de switches"""
    stack = StackForm(request.POST or None)
    if stack.is_valid():
        stack.save()
        messages.success(request, "Stack crée")
        return redirect(reverse('topologie:index-physical-grouping'))
    return form(
        {'topoform': stack, 'action_name': 'Créer'},
        'topologie/topo.html',
        request
    )


@login_required
@can_edit(Stack)
def edit_stack(request, stack, **_kwargs):
    """Edition d'un stack (nombre de switches, nom...)"""
    stack = StackForm(request.POST or None, instance=stack)
    if stack.is_valid():
        if stack.changed_data:
            stack.save()
        return redirect(reverse('topologie:index-physical-grouping'))
    return form(
        {'topoform': stack, 'action_name': 'Editer'},
        'topologie/topo.html',
        request
    )


@login_required
@can_delete(Stack)
def del_stack(request, stack, **_kwargs):
    """Supprime un stack"""
    if request.method == "POST":
        try:
            stack.delete()
            messages.success(request, "La stack a eté détruite")
        except ProtectedError:
            messages.error(
                request,
                ("La stack %s est affectée à un autre objet, impossible "
                 "de la supprimer" % stack)
            )
        return redirect(reverse('topologie:index-physical-grouping'))
    return form({'objet': stack}, 'topologie/delete.html', request)


@login_required
@can_edit(Stack)
def edit_switchs_stack(request, stack, **_kwargs):
    """Permet d'éditer la liste des switches dans une stack et l'ajouter"""

    if request.method == "POST":
        pass
    else:
        context = {'stack': stack}
        context['switchs_stack'] = stack.switchs_set.all()
        context['switchs_autres'] = Switch.object.filter(stack=None)


@login_required
@can_create(Switch)
def new_switch(request):
    """ Creation d'un switch. Cree en meme temps l'interface et la machine
    associée. Vue complexe. Appelle successivement les 4 models forms
    adaptés : machine, interface, domain et switch"""
    switch = NewSwitchForm(
        request.POST or None,
        user=request.user
    )
    interface = AddInterfaceForm(
        request.POST or None,
        user=request.user
    )
    domain = DomainForm(
        request.POST or None,
        )
    if switch.is_valid() and interface.is_valid():
        user = AssoOption.get_cached_value('utilisateur_asso')
        if not user:
            messages.error(
                request,
                ("L'user association n'existe pas encore, veuillez le "
                 "créer ou le linker dans preferences")
            )
            return redirect(reverse('topologie:index'))
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
            messages.success(request, "Le switch a été créé")
            return redirect(reverse('topologie:index'))
    i_mbf_param = generate_ipv4_mbf_param(interface, False)
    return form(
        {
            'topoform': interface,
            'machineform': switch,
            'domainform': domain,
            'i_mbf_param': i_mbf_param,
            'device': 'switch',
        },
        'topologie/topo_more.html',
        request
    )


@login_required
@can_create(Port)
def create_ports(request, switchid):
    """ Création d'une liste de ports pour un switch."""
    try:
        switch = Switch.objects.get(pk=switchid)
    except Switch.DoesNotExist:
        messages.error(request, u"Switch inexistant")
        return redirect(reverse('topologie:index'))

    s_begin = s_end = 0
    nb_ports = switch.ports.count()
    if nb_ports > 0:
        ports = switch.ports.order_by('port').values('port')
        s_begin = ports.first().get('port')
        s_end = ports.last().get('port')

    port_form = CreatePortsForm(
        request.POST or None,
        initial={'begin': s_begin, 'end': s_end}
    )

    if port_form.is_valid():
        begin = port_form.cleaned_data['begin']
        end = port_form.cleaned_data['end']
        try:
            switch.create_ports(begin, end)
            messages.success(request, "Ports créés.")
        except ValidationError as e:
            messages.error(request, ''.join(e))
        return redirect(reverse(
            'topologie:index-port',
            kwargs={'switchid': switchid}
            ))
    return form(
        {'id_switch': switchid, 'topoform': port_form},
        'topologie/switch.html',
        request
    )


@login_required
@can_edit(Switch)
def edit_switch(request, switch, switchid):
    """ Edition d'un switch. Permet de chambre nombre de ports,
    place dans le stack, interface et machine associée"""

    switch_form = EditSwitchForm(
        request.POST or None,
        instance=switch,
        user=request.user
        )
    interface_form = EditInterfaceForm(
        request.POST or None,
        instance=switch.interface_set.first(),
        user=request.user
        )
    domain_form = DomainForm(
        request.POST or None,
        instance=switch.interface_set.first().domain
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
        messages.success(request, "Le switch a bien été modifié")
        return redirect(reverse('topologie:index'))
    i_mbf_param = generate_ipv4_mbf_param(interface_form, False)
    return form(
        {
            'id_switch': switchid,
            'topoform': interface_form,
            'machineform': switch_form,
            'domainform': domain_form,
            'i_mbf_param': i_mbf_param,
            'device': 'switch',
        },
        'topologie/topo_more.html',
        request
    )


@login_required
@can_create(AccessPoint)
def new_ap(request):
    """ Creation d'une ap. Cree en meme temps l'interface et la machine
    associée. Vue complexe. Appelle successivement les 3 models forms
    adaptés : machine, interface, domain et switch"""
    ap = AddAccessPointForm(
        request.POST or None,
        user=request.user
    )
    interface = AddInterfaceForm(
        request.POST or None,
        user=request.user
    )
    domain = DomainForm(
        request.POST or None,
        )
    if ap.is_valid() and interface.is_valid():
        user = AssoOption.get_cached_value('utilisateur_asso')
        if not user:
            messages.error(
                request,
                ("L'user association n'existe pas encore, veuillez le "
                 "créer ou le linker dans preferences")
            )
            return redirect(reverse('topologie:index'))
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
            messages.success(request, "La borne a été créé")
            return redirect(reverse('topologie:index-ap'))
    i_mbf_param = generate_ipv4_mbf_param(interface, False)
    return form(
        {
            'topoform': interface,
            'machineform': ap,
            'domainform': domain,
            'i_mbf_param': i_mbf_param,
            'device': 'wifi ap',
        },
        'topologie/topo_more.html',
        request
    )


@login_required
@can_edit(AccessPoint)
def edit_ap(request, ap, **_kwargs):
    """ Edition d'un switch. Permet de chambre nombre de ports,
    place dans le stack, interface et machine associée"""
    interface_form = EditInterfaceForm(
        request.POST or None,
        user=request.user,
        instance=ap.interface_set.first()
    )
    ap_form = EditAccessPointForm(
        request.POST or None,
        user=request.user,
        instance=ap
    )
    domain_form = DomainForm(
        request.POST or None,
        instance=ap.interface_set.first().domain
        )
    if ap_form.is_valid() and interface_form.is_valid():
        user = AssoOption.get_cached_value('utilisateur_asso')
        if not user:
            messages.error(
                request,
                ("L'user association n'existe pas encore, veuillez le "
                 "créer ou le linker dans preferences")
            )
            return redirect(reverse('topologie:index-ap'))
        new_ap_obj = ap_form.save(commit=False)
        new_interface_obj = interface_form.save(commit=False)
        new_domain_obj = domain_form.save(commit=False)
        if ap_form.changed_data:
            new_ap_obj.save()
        if interface_form.changed_data:
            new_interface_obj.save()
        if domain_form.changed_data:
            new_domain_obj.save()
        messages.success(request, "La borne a été modifiée")
        return redirect(reverse('topologie:index-ap'))
    i_mbf_param = generate_ipv4_mbf_param(interface_form, False)
    return form(
        {
            'topoform': interface_form,
            'machineform': ap_form,
            'domainform': domain_form,
            'i_mbf_param': i_mbf_param,
            'device': 'wifi ap',
        },
        'topologie/topo_more.html',
        request
    )


@login_required
@can_create(Room)
def new_room(request):
    """Nouvelle chambre """
    room = EditRoomForm(request.POST or None)
    if room.is_valid():
        room.save()
        messages.success(request, "La chambre a été créé")
        return redirect(reverse('topologie:index-room'))
    return form(
        {'topoform': room, 'action_name': 'Ajouter'},
        'topologie/topo.html',
        request
    )


@login_required
@can_edit(Room)
def edit_room(request, room, **_kwargs):
    """ Edition numero et details de la chambre"""
    room = EditRoomForm(request.POST or None, instance=room)
    if room.is_valid():
        if room.changed_data:
            room.save()
            messages.success(request, "La chambre a bien été modifiée")
        return redirect(reverse('topologie:index-room'))
    return form(
        {'topoform': room, 'action_name': 'Editer'},
        'topologie/topo.html',
        request
    )


@login_required
@can_delete(Room)
def del_room(request, room, **_kwargs):
    """ Suppression d'un chambre"""
    if request.method == "POST":
        try:
            room.delete()
            messages.success(request, "La chambre/prise a été détruite")
        except ProtectedError:
            messages.error(
                request,
                ("La chambre %s est affectée à un autre objet, impossible "
                 "de la supprimer (switch ou user)" % room)
            )
        return redirect(reverse('topologie:index-room'))
    return form(
        {'objet': room, 'objet_name': 'Chambre'},
        'topologie/delete.html',
        request
    )


@login_required
@can_create(ModelSwitch)
def new_model_switch(request):
    """Nouveau modèle de switch"""
    model_switch = EditModelSwitchForm(request.POST or None)
    if model_switch.is_valid():
        model_switch.save()
        messages.success(request, "Le modèle a été créé")
        return redirect(reverse('topologie:index-model-switch'))
    return form(
        {'topoform': model_switch, 'action_name': 'Ajouter'},
        'topologie/topo.html',
        request
    )


@login_required
@can_edit(ModelSwitch)
def edit_model_switch(request, model_switch, **_kwargs):
    """ Edition d'un modèle de switch"""

    model_switch = EditModelSwitchForm(
        request.POST or None,
        instance=model_switch
    )
    if model_switch.is_valid():
        if model_switch.changed_data:
            model_switch.save()
            messages.success(request, "Le modèle a bien été modifié")
        return redirect(reverse('topologie:index-model-switch'))
    return form(
        {'topoform': model_switch, 'action_name': 'Editer'},
        'topologie/topo.html',
        request
    )


@login_required
@can_delete(ModelSwitch)
def del_model_switch(request, model_switch, **_kwargs):
    """ Suppression d'un modèle de switch"""
    if request.method == "POST":
        try:
            model_switch.delete()
            messages.success(request, "Le modèle a été détruit")
        except ProtectedError:
            messages.error(
                request,
                ("Le modèle %s est affectée à un autre objet, impossible "
                 "de la supprimer (switch ou user)" % model_switch)
            )
        return redirect(reverse('topologie:index-model-switch'))
    return form(
        {'objet': model_switch, 'objet_name': 'Modèle de switch'},
        'topologie/delete.html',
        request
    )


@login_required
@can_create(SwitchBay)
def new_switch_bay(request):
    """Nouvelle baie de switch"""
    switch_bay = EditSwitchBayForm(request.POST or None)
    if switch_bay.is_valid():
        switch_bay.save()
        messages.success(request, "La baie a été créé")
        return redirect(reverse('topologie:index-physical-grouping'))
    return form(
        {'topoform': switch_bay, 'action_name': 'Ajouter'},
        'topologie/topo.html',
        request
    )


@login_required
@can_edit(SwitchBay)
def edit_switch_bay(request, switch_bay, **_kwargs):
    """ Edition d'une baie de switch"""
    switch_bay = EditSwitchBayForm(request.POST or None, instance=switch_bay)
    if switch_bay.is_valid():
        if switch_bay.changed_data:
            switch_bay.save()
            messages.success(request, "Le switch a bien été modifié")
        return redirect(reverse('topologie:index-physical-grouping'))
    return form(
        {'topoform': switch_bay, 'action_name': 'Editer'},
        'topologie/topo.html',
        request
    )


@login_required
@can_delete(SwitchBay)
def del_switch_bay(request, switch_bay, **_kwargs):
    """ Suppression d'une baie de switch"""
    if request.method == "POST":
        try:
            switch_bay.delete()
            messages.success(request, "La baie a été détruite")
        except ProtectedError:
            messages.error(
                request,
                ("La baie %s est affecté à un autre objet, impossible "
                 "de la supprimer (switch ou user)" % switch_bay)
            )
        return redirect(reverse('topologie:index-physical-grouping'))
    return form(
        {'objet': switch_bay, 'objet_name': 'Baie de switch'},
        'topologie/delete.html',
        request
    )


@login_required
@can_create(Building)
def new_building(request):
    """Nouveau batiment"""
    building = EditBuildingForm(request.POST or None)
    if building.is_valid():
        building.save()
        messages.success(request, "Le batiment a été créé")
        return redirect(reverse('topologie:index-physical-grouping'))
    return form(
        {'topoform': building, 'action_name': 'Ajouter'},
        'topologie/topo.html',
        request
    )


@login_required
@can_edit(Building)
def edit_building(request, building, **_kwargs):
    """ Edition d'un batiment"""
    building = EditBuildingForm(request.POST or None, instance=building)
    if building.is_valid():
        if building.changed_data:
            building.save()
            messages.success(request, "Le batiment a bien été modifié")
        return redirect(reverse('topologie:index-physical-grouping'))
    return form(
        {'topoform': building, 'action_name': 'Editer'},
        'topologie/topo.html',
        request
    )


@login_required
@can_delete(Building)
def del_building(request, building, **_kwargs):
    """ Suppression d'un batiment"""
    if request.method == "POST":
        try:
            building.delete()
            messages.success(request, "La batiment a été détruit")
        except ProtectedError:
            messages.error(
                request,
                ("Le batiment %s est affecté à un autre objet, impossible "
                 "de la supprimer (switch ou user)" % building)
            )
        return redirect(reverse('topologie:index-physical-grouping'))
    return form(
        {'objet': building, 'objet_name': 'Bâtiment'},
        'topologie/delete.html',
        request
    )


@login_required
@can_create(ConstructorSwitch)
def new_constructor_switch(request):
    """Nouveau constructeur de switch"""
    constructor_switch = EditConstructorSwitchForm(request.POST or None)
    if constructor_switch.is_valid():
        constructor_switch.save()
        messages.success(request, "Le constructeur a été créé")
        return redirect(reverse('topologie:index-model-switch'))
    return form(
        {'topoform': constructor_switch, 'action_name': 'Ajouter'},
        'topologie/topo.html',
        request
    )


@login_required
@can_edit(ConstructorSwitch)
def edit_constructor_switch(request, constructor_switch, **_kwargs):
    """ Edition d'un constructeur de switch"""

    constructor_switch = EditConstructorSwitchForm(
        request.POST or None,
        instance=constructor_switch
    )
    if constructor_switch.is_valid():
        if constructor_switch.changed_data:
            constructor_switch.save()
            messages.success(request, "Le modèle a bien été modifié")
        return redirect(reverse('topologie:index-model-switch'))
    return form(
        {'topoform': constructor_switch, 'action_name': 'Editer'},
        'topologie/topo.html',
        request
    )


@login_required
@can_delete(ConstructorSwitch)
def del_constructor_switch(request, constructor_switch, **_kwargs):
    """ Suppression d'un constructeur de switch"""
    if request.method == "POST":
        try:
            constructor_switch.delete()
            messages.success(request, "Le constructeur a été détruit")
        except ProtectedError:
            messages.error(
                request,
                ("Le constructeur %s est affecté à un autre objet, impossible "
                 "de la supprimer (switch ou user)" % constructor_switch)
            )
        return redirect(reverse('topologie:index-model-switch'))
    return form({
        'objet': constructor_switch,
        'objet_name': 'Constructeur de switch'
        }, 'topologie/delete.html', request)


@login_required
@can_create(PortProfile)
def new_port_profile(request):
    """Create a new port profile"""
    port_profile = EditPortProfileForm(request.POST or None)
    if port_profile.is_valid():
        port_profile.save()
        messages.success(request, _("Port profile created"))
        return redirect(reverse('topologie:index'))
    return form(
        {'topoform': port_profile, 'action_name': _("Create")},
        'topologie/topo.html',
        request
    )


@login_required
@can_edit(PortProfile)
def edit_port_profile(request, port_profile, **_kwargs):
    """Edit a port profile"""
    port_profile = EditPortProfileForm(request.POST or None, instance=port_profile)
    if port_profile.is_valid():
        if port_profile.changed_data:
            port_profile.save()
            messages.success(request, _("Port profile modified"))
        return redirect(reverse('topologie:index'))
    return form(
        {'topoform': port_profile, 'action_name': _("Edit")},
        'topologie/topo.html',
        request
    )



@login_required
@can_delete(PortProfile)
def del_port_profile(request, port_profile, **_kwargs):
    """Delete a port profile"""
    if request.method == 'POST':
        try:
            port_profile.delete()
            messages.success(request, 
                _("The port profile was successfully deleted"))
        except ProtectedError:
            messages.success(request, 
                _("Impossible to delete the port profile"))
        return redirect(reverse('topologie:index'))
    return form(
            {'objet': port_profile, 'objet_name': _("Port profile")},
            'topologie/delete.html',
            request
    )

def make_machine_graph():
    """
    Create the graph of switchs, machines and access points.
    """
    dico = {
        'subs': [],
        'links' : [],
        'alone': [],
        'colors': {
            'head': "#7f0505",  # Color parameters for the graph
            'back': "#b5adad",
            'texte': "#563d01",
            'border_bornes': "#02078e",
            'head_bornes': "#25771c",
            'head_server': "#1c3777"
            }
        }
    missing = list(Switch.objects.all())
    detected = []
    for building in Building.objects.all():  # Visit all buildings

        dico['subs'].append(
            {
            'bat_id': building.id,
            'bat_name': building,
            'switchs': [],
            'bornes': [],
            'machines': []
            }
        )
        # Visit all switchs in this building
        for switch in Switch.objects.filter(switchbay__building=building):   
            dico['subs'][-1]['switchs'].append({
                'name': switch.main_interface().domain.name,
                'nombre': switch.number,
                'model': switch.model,
                'id': switch.id,
                'batiment': building,
                'ports': []
            })
            # visit all ports of this switch and add the switchs linked to it
            for port in switch.ports.filter(related__isnull=False): 
                dico['subs'][-1]['switchs'][-1]['ports'].append({
                    'numero': port.port,
                    'related': port.related.switch.main_interface().domain.name
                })

        for ap in AccessPoint.all_ap_in(building):
            dico['subs'][-1]['bornes'].append({
                'name': ap.short_name,
                'switch': ap.switch()[0].main_interface().domain.name,
                'port': ap.switch()[0].ports.filter(
                    machine_interface__machine=ap
                )[0].port
            })
        for server in Server.all_server_in(building):
            dico['subs'][-1]['machines'].append({
                'name': server.short_name,
                'switch': server.switch()[0].main_interface().domain.name,
                'port': Port.objects.filter(machine_interface__machine=server)[0].port
            })

    # While the list of forgotten ones is not empty
    while missing:
        if missing[0].ports.count():  # The switch is not empty
            links, new_detected = recursive_switchs(missing[0], None, [missing[0]])
            for link in links:
                dico['links'].append(link)
            # Update the lists of missings and already detected switchs
            missing=[i for i in missing if i not in new_detected]
            detected += new_detected
        else:  # If the switch have no ports, don't explore it and hop to the next one
            del missing[0]
    # Switchs that are not connected or not in a building
    for switch in Switch.objects.filter(switchbay__isnull=True).exclude(ports__related__isnull=False):
        dico['alone'].append({
            'id': switch.id,
            'name': switch.main_interface().domain.name
            })


    dot_data=generate_dot(dico,'topologie/graph_switch.dot')  # generate the dot file

    f = tempfile.NamedTemporaryFile(mode='w+', encoding='utf-8', delete=False)  # Create a temporary file to store the dot data
    with f:
            f.write(dot_data)
    unflatten = Popen(  # unflatten the graph to make it look better
            ["unflatten","-l", "3", f.name],
        stdout=PIPE
    )
    image = Popen(  # pipe the result of the first command into the second
        ["dot", "-Tpng", "-o", MEDIA_ROOT + "/images/switchs.png"],
        stdin=unflatten.stdout,
        stdout=PIPE
    )

def generate_dot(data,template):
    """create the dot file
    :param data: dictionary passed to the template
    :param template: path to the dot template
    :return: all the lines of the dot file"""
    t = loader.get_template(template)
    if not isinstance(t, Template) and not (hasattr(t, 'template') and isinstance(t.template, Template)):
        raise Exception("Le template par défaut de Django n'est pas utilisé."
                        "Cela peut mener à des erreurs de rendu."
                        "Vérifiez les paramètres")
    c = Context(data).flatten()
    dot = t.render(c)
    return(dot)

def recursive_switchs(switch_start, switch_before, detected):
    """Visit the switch and travel to the switchs linked to it.
    :param switch_start: the switch to begin the visit on
    :param switch_before: the switch that you come from. None if switch_start is the first one
    :param detected: list of all switchs already visited. None if switch_start is the first one
    :return: A list of all the links found and a list of all the switchs visited"""
    detected.append(switch_start)
    links_return=[]  # list of dictionaries of the links to be detected
    for port in switch_start.ports.filter(related__isnull=False):  # create links to every switchs below
        if port.related.switch != switch_before and port.related.switch != port.switch and port.related.switch not in detected:  # Not the switch that we come from, not the current switch
            links = {  # Dictionary of a link
                'depart':switch_start.id,
                'arrive':port.related.switch.id
            }
            links_return.append(links)  # Add current and below levels links

    for port in switch_start.ports.filter(related__isnull=False):  # go down on every related switchs
        if port.related.switch not in detected:  # The switch at the end of this link has not been visited
            links_down, detected = recursive_switchs(port.related.switch, switch_start, detected)  # explore it and get the results
            for link in links_down:  # Add the non empty links to the current list
                if link:
                    links_return.append(link) 
    return (links_return, detected)

