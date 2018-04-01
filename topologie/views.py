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
from django.contrib.auth.decorators import login_required, permission_required
from django.db import IntegrityError
from django.db import transaction
from django.db.models import ProtectedError, Prefetch
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from reversion import revisions as reversion
from reversion.models import Version

from topologie.models import (
    Switch,
    Port,
    Room,
    Stack,
    ModelSwitch,
    ConstructorSwitch,
    AccessPoint
)
from topologie.forms import EditPortForm, NewSwitchForm, EditSwitchForm
from topologie.forms import (
    AddPortForm,
    EditRoomForm,
    StackForm,
    EditModelSwitchForm,
    EditConstructorSwitchForm,
    CreatePortsForm,
    AddAccessPointForm,
    EditAccessPointForm
)
from users.views import form
from re2o.utils import SortTable
from re2o.acl import (
    can_create,
    can_edit,
    can_delete,
    can_view,
    can_view_all,
)
from machines.forms import (
    DomainForm,
    NewMachineForm,
    EditMachineForm,
    EditInterfaceForm,
    AddInterfaceForm
)
from machines.views import generate_ipv4_mbf_param
from machines.models import Interface
from preferences.models import AssoOption, GeneralOption


@login_required
@can_view_all(Switch)
def index(request):
    """ Vue d'affichage de tous les swicthes"""
    switch_list = Switch.objects\
        .prefetch_related(Prefetch(
            'interface_set',
        queryset=Interface.objects.select_related('ipv4__ip_type__extension').select_related('domain__extension')
        ))\
        .select_related('stack')
    switch_list = SortTable.sort(
        switch_list,
        request.GET.get('col'),
        request.GET.get('order'),
        SortTable.TOPOLOGIE_INDEX
    )
    pagination_number = GeneralOption.get_cached_value('pagination_number')
    paginator = Paginator(switch_list, pagination_number)
    page = request.GET.get('page')
    try:
        switch_list = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        switch_list = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        switch_list = paginator.page(paginator.num_pages)
    return render(request, 'topologie/index.html', {
        'switch_list': switch_list
        })


@login_required
@can_view_all(Port)
@can_view(Switch)
def index_port(request, switch, switchid):
    """ Affichage de l'ensemble des ports reliés à un switch particulier"""
    port_list = Port.objects.filter(switch=switch)\
        .select_related('room')\
        .select_related('machine_interface__domain__extension')\
        .select_related('machine_interface__machine__user')\
        .select_related('related__switch')\
        .prefetch_related(Prefetch(
            'related__switch__interface_set',
            queryset=Interface.objects.select_related('domain__extension')
        ))\
        .select_related('switch')
    port_list = SortTable.sort(
        port_list,
        request.GET.get('col'),
        request.GET.get('order'),
        SortTable.TOPOLOGIE_INDEX_PORT
    )
    return render(request, 'topologie/index_p.html', {
        'port_list': port_list,
        'id_switch': switchid,
        'nom_switch': switch
        })


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
    paginator = Paginator(room_list, pagination_number)
    page = request.GET.get('page')
    try:
        room_list = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        room_list = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        room_list = paginator.page(paginator.num_pages)
    return render(request, 'topologie/index_room.html', {
        'room_list': room_list
        })


@login_required
@can_view_all(AccessPoint)
def index_ap(request):
    """ Affichage de l'ensemble des bornes"""
    ap_list = AccessPoint.objects\
        .prefetch_related(Prefetch(
            'interface_set',
            queryset=Interface.objects.select_related('ipv4__ip_type__extension').select_related('domain__extension')
        ))
    ap_list = SortTable.sort(
        ap_list,
        request.GET.get('col'),
        request.GET.get('order'),
        SortTable.TOPOLOGIE_INDEX_BORNE
    )
    pagination_number = GeneralOption.get_cached_value('pagination_number')
    paginator = Paginator(ap_list, pagination_number)
    page = request.GET.get('page')
    try:
        ap_list = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        ap_list = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        ap_list = paginator.page(paginator.num_pages)
    return render(request, 'topologie/index_ap.html', {
        'ap_list': ap_list
        })


@login_required
@can_view_all(Stack)
def index_stack(request):
    """Affichage de la liste des stacks (affiche l'ensemble des switches)"""
    stack_list = Stack.objects\
        .prefetch_related('switch_set__interface_set__domain__extension')
    stack_list = SortTable.sort(
        stack_list,
        request.GET.get('col'),
        request.GET.get('order'),
        SortTable.TOPOLOGIE_INDEX_STACK
    )
    return render(request, 'topologie/index_stack.html', {
        'stack_list': stack_list
        })


@login_required
@can_view_all(ModelSwitch)
@can_view_all(ConstructorSwitch)
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
    return render(request, 'topologie/index_model_switch.html', {
        'model_switch_list': model_switch_list,
        'constructor_switch_list': constructor_switch_list,
        })


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
            with transaction.atomic(), reversion.create_revision():
                port.save()
                reversion.set_user(request.user)
                reversion.set_comment("Création")
            messages.success(request, "Port ajouté")
        except IntegrityError:
            messages.error(request, "Ce port existe déjà")
        return redirect(reverse(
            'topologie:index-port',
            kwargs={'switchid':switchid}
            ))
    return form({'id_switch': switchid,'topoform': port, 'action_name' : 'Ajouter'}, 'topologie/topo.html', request)


@login_required
@can_edit(Port)
def edit_port(request, port_object, portid):
    """ Edition d'un port. Permet de changer le switch parent et
    l'affectation du port"""

    port = EditPortForm(request.POST or None, instance=port_object)
    if port.is_valid():
        with transaction.atomic(), reversion.create_revision():
            port.save()
            reversion.set_user(request.user)
            reversion.set_comment("Champs modifié(s) : %s" % ', '.join(
                field for field in port.changed_data
                ))
        messages.success(request, "Le port a bien été modifié")
        return redirect(reverse(
            'topologie:index-port',
            kwargs={'switchid': str(port_object.switch.id)}
            ))
    return form({'id_switch': str(port_object.switch.id), 'topoform': port, 'action_name' : 'Editer'}, 'topologie/topo.html', request)


@login_required
@can_delete(Port)
def del_port(request, port, portid):
    """ Supprime le port"""
    if request.method == "POST":
        try:
            with transaction.atomic(), reversion.create_revision():
                port.delete()
                reversion.set_user(request.user)
                reversion.set_comment("Destruction")
                messages.success(request, "Le port a été détruit")
        except ProtectedError:
            messages.error(request, "Le port %s est affecté à un autre objet,\
                impossible de le supprimer" % port)
        return redirect(reverse(
            'topologie:index-port',
            kwargs={'switchid':str(port.switch.id)}
            ))
    return form({'objet': port}, 'topologie/delete.html', request)


@login_required
@can_create(Stack)
def new_stack(request):
    """Ajoute un nouveau stack : stackid_min, max, et nombre de switches"""
    stack = StackForm(request.POST or None)
    if stack.is_valid():
        with transaction.atomic(), reversion.create_revision():
            stack.save()
            reversion.set_user(request.user)
            reversion.set_comment("Création")
        messages.success(request, "Stack crée")
    return form({'topoform': stack, 'action_name' : 'Créer'}, 'topologie/topo.html', request)


@login_required
@can_edit(Stack)
def edit_stack(request, stack, stackid):
    """Edition d'un stack (nombre de switches, nom...)"""

    stack = StackForm(request.POST or None, instance=stack)
    if stack.is_valid():
        with transaction.atomic(), reversion.create_revision():
            stack.save()
            reversion.set_user(request.user)
            reversion.set_comment(
                "Champs modifié(s) : %s" % ', '.join(
                    field for field in stack.changed_data
                    )
                )
            return redirect(reverse('topologie:index-stack'))
    return form({'topoform': stack, 'action_name' : 'Editer'}, 'topologie/topo.html', request)


@login_required
@can_delete(Stack)
def del_stack(request, stack, stackid):
    """Supprime un stack"""
    if request.method == "POST":
        try:
            with transaction.atomic(), reversion.create_revision():
                stack.delete()
                reversion.set_user(request.user)
                reversion.set_comment("Destruction")
                messages.success(request, "La stack a eté détruite")
        except ProtectedError:
            messages.error(request, "La stack %s est affectée à un autre\
                objet, impossible de la supprimer" % stack)
        return redirect(reverse('topologie:index-stack'))
    return form({'objet': stack}, 'topologie/delete.html', request)


@login_required
@can_edit(Stack)
def edit_switchs_stack(request, stack, stackid):
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
            messages.error(request, "L'user association n'existe pas encore,\
            veuillez le créer ou le linker dans preferences")
            return redirect(reverse('topologie:index'))
        new_switch = switch.save(commit=False)
        new_switch.user = user
        new_interface_instance = interface.save(commit=False)
        domain.instance.interface_parent = new_interface_instance
        if domain.is_valid():
            new_domain_instance = domain.save(commit=False)
            with transaction.atomic(), reversion.create_revision():
                new_switch.save()
                reversion.set_user(request.user)
                reversion.set_comment("Création")
            new_interface_instance.machine = new_switch
            with transaction.atomic(), reversion.create_revision():
                new_interface_instance.save()
                reversion.set_user(request.user)
                reversion.set_comment("Création")
            new_domain_instance.interface_parent = new_interface_instance
            with transaction.atomic(), reversion.create_revision():
                new_domain_instance.save()
                reversion.set_user(request.user)
                reversion.set_comment("Création")
            messages.success(request, "Le switch a été créé")
            return redirect(reverse('topologie:index'))
    i_mbf_param = generate_ipv4_mbf_param(interface, False)
    return form({
        'topoform': interface,
        'machineform': switch,
        'domainform': domain,
        'i_mbf_param': i_mbf_param,
        'device' : 'switch',
        }, 'topologie/topo_more.html', request)


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
            kwargs={'switchid':switchid}
            ))
    return form({'id_switch': switchid, 'topoform': port_form}, 'topologie/switch.html', request)


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
        new_switch = switch_form.save(commit=False)
        new_interface_instance = interface_form.save(commit=False)
        new_domain = domain_form.save(commit=False)
        with transaction.atomic(), reversion.create_revision():
            new_switch.save()
            reversion.set_user(request.user)
            reversion.set_comment(
                "Champs modifié(s) : %s" % ', '.join(
                    field for field in switch_form.changed_data
                    )
                )
        with transaction.atomic(), reversion.create_revision():
            new_interface_instance.save()
            reversion.set_user(request.user)
            reversion.set_comment("Champs modifié(s) : %s" % ', '.join(
                field for field in interface_form.changed_data)
                                 )
        with transaction.atomic(), reversion.create_revision():
            new_domain.save()
            reversion.set_user(request.user)
            reversion.set_comment("Champs modifié(s) : %s" % ', '.join(
                field for field in domain_form.changed_data)
                                 )
        messages.success(request, "Le switch a bien été modifié")
        return redirect(reverse('topologie:index'))
    i_mbf_param = generate_ipv4_mbf_param(interface_form, False )
    return form({
        'id_switch': switchid,
        'topoform': interface_form,
        'machineform': switch_form,
        'domainform': domain_form,
        'i_mbf_param': i_mbf_param,
        'device' : 'switch',
        }, 'topologie/topo_more.html', request)


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
            messages.error(request, "L'user association n'existe pas encore,\
            veuillez le créer ou le linker dans preferences")
            return redirect(reverse('topologie:index'))
        new_ap = ap.save(commit=False)
        new_ap.user = user
        new_interface = interface.save(commit=False)
        domain.instance.interface_parent = new_interface
        if domain.is_valid():
            new_domain_instance = domain.save(commit=False)
            with transaction.atomic(), reversion.create_revision():
                new_ap.save()
                reversion.set_user(request.user)
                reversion.set_comment("Création")
            new_interface.machine = new_ap
            with transaction.atomic(), reversion.create_revision():
                new_interface.save()
                reversion.set_user(request.user)
                reversion.set_comment("Création")
            new_domain_instance.interface_parent = new_interface
            with transaction.atomic(), reversion.create_revision():
                new_domain_instance.save()
                reversion.set_user(request.user)
                reversion.set_comment("Création")
            messages.success(request, "La borne a été créé")
            return redirect(reverse('topologie:index-ap'))
    i_mbf_param = generate_ipv4_mbf_param(interface, False)
    return form({
        'topoform': interface,
        'machineform': ap,
        'domainform': domain,
        'i_mbf_param': i_mbf_param,
        'device' : 'wifi ap',
        }, 'topologie/topo_more.html', request)


@login_required
@can_edit(AccessPoint)
def edit_ap(request, ap, accesspointid):
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
            messages.error(request, "L'user association n'existe pas encore,\
            veuillez le créer ou le linker dans preferences")
            return redirect(reverse('topologie:index-ap'))
        new_ap = ap_form.save(commit=False)
        new_interface = interface_form.save(commit=False)
        new_domain = domain_form.save(commit=False)
        with transaction.atomic(), reversion.create_revision():
            new_ap.save()
            reversion.set_user(request.user)
            reversion.set_comment(
                "Champs modifié(s) : %s" % ', '.join(
                    field for field in ap_form.changed_data)
            )
        with transaction.atomic(), reversion.create_revision():
            new_interface.save()
            reversion.set_user(request.user)
            reversion.set_comment("Champs modifié(s) : %s" % ', '.join(
                field for field in interface_form.changed_data)
            )
            reversion.set_comment("Création")
        with transaction.atomic(), reversion.create_revision():
            new_domain.save()
            reversion.set_user(request.user)
            reversion.set_comment("Champs modifié(s) : %s" % ', '.join(
                field for field in domain_form.changed_data)
            )
        messages.success(request, "La borne a été modifiée")
        return redirect(reverse('topologie:index-ap'))
    i_mbf_param = generate_ipv4_mbf_param(interface_form, False )
    return form({
        'topoform': interface_form,
        'machineform': ap_form,
        'domainform': domain_form,
        'i_mbf_param': i_mbf_param,
        'device' : 'wifi ap',
        }, 'topologie/topo_more.html', request)
    

@login_required
@can_create(Room)
def new_room(request):
    """Nouvelle chambre """
    room = EditRoomForm(request.POST or None)
    if room.is_valid():
        with transaction.atomic(), reversion.create_revision():
            room.save()
            reversion.set_user(request.user)
            reversion.set_comment("Création")
        messages.success(request, "La chambre a été créé")
        return redirect(reverse('topologie:index-room'))
    return form({'topoform': room, 'action_name' : 'Ajouter'}, 'topologie/topo.html', request)


@login_required
@can_edit(Room)
def edit_room(request, room, roomid):
    """ Edition numero et details de la chambre"""

    room = EditRoomForm(request.POST or None, instance=room)
    if room.is_valid():
        with transaction.atomic(), reversion.create_revision():
            room.save()
            reversion.set_user(request.user)
            reversion.set_comment("Champs modifié(s) : %s" % ', '.join(
                field for field in room.changed_data)
                                 )
        messages.success(request, "La chambre a bien été modifiée")
        return redirect(reverse('topologie:index-room'))
    return form({'topoform': room, 'action_name' : 'Editer'}, 'topologie/topo.html', request)


@login_required
@can_delete(Room)
def del_room(request, room, roomid):
    """ Suppression d'un chambre"""
    if request.method == "POST":
        try:
            with transaction.atomic(), reversion.create_revision():
                room.delete()
                reversion.set_user(request.user)
                reversion.set_comment("Destruction")
                messages.success(request, "La chambre/prise a été détruite")
        except ProtectedError:
            messages.error(request, "La chambre %s est affectée à un autre objet,\
                impossible de la supprimer (switch ou user)" % room)
        return redirect(reverse('topologie:index-room'))
    return form({
        'objet': room,
        'objet_name': 'Chambre'
        }, 'topologie/delete.html', request)


@login_required
@can_create(ModelSwitch)
def new_model_switch(request):
    """Nouveau modèle de switch"""
    model_switch = EditModelSwitchForm(request.POST or None)
    if model_switch.is_valid():
        with transaction.atomic(), reversion.create_revision():
            model_switch.save()
            reversion.set_user(request.user)
            reversion.set_comment("Création")
        messages.success(request, "Le modèle a été créé")
        return redirect(reverse('topologie:index-model-switch'))
    return form({'topoform': model_switch, 'action_name' : 'Ajouter'}, 'topologie/topo.html', request)


@login_required
@can_edit(ModelSwitch)
def edit_model_switch(request, model_switch, modelswitchid):
    """ Edition d'un modèle de switch"""

    model_switch = EditModelSwitchForm(request.POST or None, instance=model_switch)
    if model_switch.is_valid():
        with transaction.atomic(), reversion.create_revision():
            model_switch.save()
            reversion.set_user(request.user)
            reversion.set_comment("Champs modifié(s) : %s" % ', '.join(
                field for field in model_switch.changed_data)
            )
        messages.success(request, "Le modèle a bien été modifié")
        return redirect(reverse('topologie:index-model-switch'))
    return form({'topoform': model_switch, 'action_name' : 'Editer'}, 'topologie/topo.html', request)


@login_required
@can_delete(ModelSwitch)
def del_model_switch(request, model_switch, modelswitchid):
    """ Suppression d'un modèle de switch"""
    if request.method == "POST":
        try:
            with transaction.atomic(), reversion.create_revision():
                model_switch.delete()
                reversion.set_user(request.user)
                reversion.set_comment("Destruction")
                messages.success(request, "Le modèle a été détruit")
        except ProtectedError:
            messages.error(request, "Le modèle %s est affectée à un autre objet,\
                impossible de la supprimer (switch ou user)" % model_switch)
        return redirect(reverse('topologie:index-model-switch'))
    return form({
        'objet': model_switch,
        'objet_name': 'Modèle de switch'
        }, 'topologie/delete.html', request)


@login_required
@can_create(ConstructorSwitch)
def new_constructor_switch(request):
    """Nouveau constructeur de switch"""
    constructor_switch = EditConstructorSwitchForm(request.POST or None)
    if constructor_switch.is_valid():
        with transaction.atomic(), reversion.create_revision():
            constructor_switch.save()
            reversion.set_user(request.user)
            reversion.set_comment("Création")
        messages.success(request, "Le constructeur a été créé")
        return redirect(reverse('topologie:index-model-switch'))
    return form({'topoform': constructor_switch, 'action_name' : 'Ajouter'}, 'topologie/topo.html', request)


@login_required
@can_edit(ConstructorSwitch)
def edit_constructor_switch(request, constructor_switch, constructorswitchid):
    """ Edition d'un constructeur de switch"""

    constructor_switch = EditConstructorSwitchForm(request.POST or None, instance=constructor_switch)
    if constructor_switch.is_valid():
        with transaction.atomic(), reversion.create_revision():
            constructor_switch.save()
            reversion.set_user(request.user)
            reversion.set_comment("Champs modifié(s) : %s" % ', '.join(
                field for field in constructor_switch.changed_data)
            )
        messages.success(request, "Le modèle a bien été modifié")
        return redirect(reverse('topologie:index-model-switch'))
    return form({'topoform': constructor_switch, 'action_name' : 'Editer'}, 'topologie/topo.html', request)


@login_required
@can_delete(ConstructorSwitch)
def del_constructor_switch(request, constructor_switch, constructorswitchid):
    """ Suppression d'un constructeur de switch"""
    if request.method == "POST":
        try:
            with transaction.atomic(), reversion.create_revision():
                constructor_switch.delete()
                reversion.set_user(request.user)
                reversion.set_comment("Destruction")
                messages.success(request, "Le constructeur a été détruit")
        except ProtectedError:
            messages.error(request, "Le constructeur %s est affecté à un autre objet,\
                impossible de la supprimer (switch ou user)" % constructor_switch)
        return redirect(reverse('topologie:index-model-switch'))
    return form({
        'objet': constructor_switch,
        'objet_name': 'Constructeur de switch'
        }, 'topologie/delete.html', request)
