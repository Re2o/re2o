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

import itertools

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.db import IntegrityError
from django.db import transaction
from django.db.models import ProtectedError
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from reversion import revisions as reversion
from reversion.models import Version

from topologie.models import Switch, Port, Room, Stack
from topologie.forms import EditPortForm, NewSwitchForm, EditSwitchForm
from topologie.forms import AddPortForm, EditRoomForm, StackForm
from topologie.forms import CreatePortsForm
from users.views import form
from re2o.utils import SortTable
from machines.forms import (
    DomainForm,
    NewMachineForm,
    EditMachineForm,
    EditInterfaceForm,
    AddInterfaceForm
)
from machines.views import generate_ipv4_mbf_param
from preferences.models import AssoOption, GeneralOption


@login_required
@permission_required('cableur')
def index(request):
    """ Vue d'affichage de tous les swicthes"""
    switch_list = Switch.objects\
        .select_related('switch_interface__domain__extension')\
        .select_related('switch_interface__ipv4')\
        .select_related('switch_interface__domain')\
        .select_related('stack')
    switch_list = SortTable.sort(
        switch_list,
        request.GET.get('col'),
        request.GET.get('order'),
        SortTable.TOPOLOGIE_INDEX
    )
    return render(request, 'topologie/index.html', {
        'switch_list': switch_list
        })


@login_required
@permission_required('cableur')
def history(request, object_name, object_id):
    """ Vue générique pour afficher l'historique complet d'un objet"""
    if object_name == 'switch':
        try:
            object_instance = Switch.objects.get(pk=object_id)
        except Switch.DoesNotExist:
            messages.error(request, "Switch inexistant")
            return redirect("/topologie/")
    elif object_name == 'port':
        try:
            object_instance = Port.objects.get(pk=object_id)
        except Port.DoesNotExist:
            messages.error(request, "Port inexistant")
            return redirect("/topologie/")
    elif object_name == 'room':
        try:
            object_instance = Room.objects.get(pk=object_id)
        except Room.DoesNotExist:
            messages.error(request, "Chambre inexistante")
            return redirect("/topologie/")
    elif object_name == 'stack':
        try:
            object_instance = Stack.objects.get(pk=object_id)
        except Room.DoesNotExist:
            messages.error(request, "Stack inexistante")
            return redirect("/topologie/")
    else:
        messages.error(request, "Objet  inconnu")
        return redirect("/topologie/")
    options, _created = GeneralOption.objects.get_or_create()
    pagination_number = options.pagination_number
    reversions = Version.objects.get_for_object(object_instance)
    paginator = Paginator(reversions, pagination_number)
    page = request.GET.get('page')
    try:
        reversions = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        reversions = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        reversions = paginator.page(paginator.num_pages)
    return render(request, 're2o/history.html', {
        'reversions': reversions,
        'object': object_instance
        })


@login_required
@permission_required('cableur')
def index_port(request, switch_id):
    """ Affichage de l'ensemble des ports reliés à un switch particulier"""
    try:
        switch = Switch.objects.get(pk=switch_id)
    except Switch.DoesNotExist:
        messages.error(request, u"Switch inexistant")
        return redirect("/topologie/")
    port_list = Port.objects.filter(switch=switch)\
        .select_related('room')\
        .select_related('machine_interface__domain__extension')\
        .select_related('machine_interface__machine__user')\
        .select_related(
            'related__switch__switch_interface__domain__extension'
        )\
        .select_related('switch')
    port_list = SortTable.sort(
        port_list,
        request.GET.get('col'),
        request.GET.get('order'),
        SortTable.TOPOLOGIE_INDEX_PORT
    )
    return render(request, 'topologie/index_p.html', {
        'port_list': port_list,
        'id_switch': switch_id,
        'nom_switch': switch
        })


@login_required
@permission_required('cableur')
def index_room(request):
    """ Affichage de l'ensemble des chambres"""
    room_list = Room.objects
    room_list = SortTable.sort(
        room_list,
        request.GET.get('col'),
        request.GET.get('order'),
        SortTable.TOPOLOGIE_INDEX_ROOM
    )
    options, _created = GeneralOption.objects.get_or_create()
    pagination_number = options.pagination_number
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
@permission_required('infra')
def index_stack(request):
    """Affichage de la liste des stacks (affiche l'ensemble des switches)"""
    stack_list = Stack.objects\
        .prefetch_related('switch_set__switch_interface__domain__extension')
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
@permission_required('infra')
def new_port(request, switch_id):
    """ Nouveau port"""
    try:
        switch = Switch.objects.get(pk=switch_id)
    except Switch.DoesNotExist:
        messages.error(request, u"Switch inexistant")
        return redirect("/topologie/")
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
        return redirect("/topologie/switch/" + switch_id)
    return form({'topoform': port}, 'topologie/topo.html', request)


@login_required
@permission_required('infra')
def edit_port(request, port_id):
    """ Edition d'un port. Permet de changer le switch parent et
    l'affectation du port"""
    try:
        port_object = Port.objects\
            .select_related('switch__switch_interface__domain__extension')\
            .select_related('machine_interface__domain__extension')\
            .select_related('machine_interface__switch')\
            .select_related('room')\
            .select_related('related')\
            .get(pk=port_id)
    except Port.DoesNotExist:
        messages.error(request, u"Port inexistant")
        return redirect("/topologie/")
    port = EditPortForm(request.POST or None, instance=port_object)
    if port.is_valid():
        with transaction.atomic(), reversion.create_revision():
            port.save()
            reversion.set_user(request.user)
            reversion.set_comment("Champs modifié(s) : %s" % ', '.join(
                field for field in port.changed_data
                ))
        messages.success(request, "Le port a bien été modifié")
        return redirect("/topologie/switch/" + str(port_object.switch.id))
    return form({'topoform': port}, 'topologie/topo.html', request)


@login_required
@permission_required('infra')
def del_port(request, port_id):
    """ Supprime le port"""
    try:
        port = Port.objects.get(pk=port_id)
    except Port.DoesNotExist:
        messages.error(request, u"Port inexistant")
        return redirect('/topologie/')
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
        return redirect('/topologie/switch/' + str(port.switch.id))
    return form({'objet': port}, 'topologie/delete.html', request)


@login_required
@permission_required('infra')
def new_stack(request):
    """Ajoute un nouveau stack : stack_id_min, max, et nombre de switches"""
    stack = StackForm(request.POST or None)
    if stack.is_valid():
        with transaction.atomic(), reversion.create_revision():
            stack.save()
            reversion.set_user(request.user)
            reversion.set_comment("Création")
        messages.success(request, "Stack crée")
    return form({'topoform': stack}, 'topologie/topo.html', request)


@login_required
@permission_required('infra')
def edit_stack(request, stack_id):
    """Edition d'un stack (nombre de switches, nom...)"""
    try:
        stack = Stack.objects.get(pk=stack_id)
    except Stack.DoesNotExist:
        messages.error(request, u"Stack inexistante")
        return redirect('/topologie/index_stack/')
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
        return redirect('/topologie/index_stack')
    return form({'topoform': stack}, 'topologie/topo.html', request)


@login_required
@permission_required('infra')
def del_stack(request, stack_id):
    """Supprime un stack"""
    try:
        stack = Stack.objects.get(pk=stack_id)
    except Stack.DoesNotExist:
        messages.error(request, u"Stack inexistante")
        return redirect('/topologie/index_stack')
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
        return redirect('/topologie/index_stack')
    return form({'objet': stack}, 'topologie/delete.html', request)


@login_required
@permission_required('infra')
def edit_switchs_stack(request, stack_id):
    """Permet d'éditer la liste des switches dans une stack et l'ajouter"""
    try:
        stack = Stack.objects.get(pk=stack_id)
    except Stack.DoesNotExist:
        messages.error(request, u"Stack inexistante")
        return redirect('/topologie/index_stack')
    if request.method == "POST":
        pass
    else:
        context = {'stack': stack}
        context['switchs_stack'] = stack.switchs_set.all()
        context['switchs_autres'] = Switch.object.filter(stack=None)


@login_required
@permission_required('infra')
def new_switch(request):
    """ Creation d'un switch. Cree en meme temps l'interface et la machine
    associée. Vue complexe. Appelle successivement les 4 models forms
    adaptés : machine, interface, domain et switch"""
    switch = NewSwitchForm(request.POST or None)
    machine = NewMachineForm(request.POST or None)
    interface = AddInterfaceForm(
        request.POST or None,
        infra=request.user.has_perms(('infra',))
        )
    domain = DomainForm(
        request.POST or None,
        )
    if switch.is_valid() and machine.is_valid() and interface.is_valid():
        options, _created = AssoOption.objects.get_or_create()
        user = options.utilisateur_asso
        if not user:
            messages.error(request, "L'user association n'existe pas encore,\
            veuillez le créer ou le linker dans preferences")
            return redirect("/topologie/")
        new_machine = machine.save(commit=False)
        new_machine.user = user
        new_interface = interface.save(commit=False)
        new_switch_instance = switch.save(commit=False)
        new_domain_instance = domain.save(commit=False)
        with transaction.atomic(), reversion.create_revision():
            new_machine.save()
            reversion.set_user(request.user)
            reversion.set_comment("Création")
        new_interface.machine = new_machine
        with transaction.atomic(), reversion.create_revision():
            new_interface.save()
            reversion.set_user(request.user)
            reversion.set_comment("Création")
        new_domain_instance.interface_parent = new_interface
        with transaction.atomic(), reversion.create_revision():
            new_domain_instance.save()
            reversion.set_user(request.user)
            reversion.set_comment("Création")
        new_switch_instance.switch_interface = new_interface
        with transaction.atomic(), reversion.create_revision():
            new_switch_instance.save()
            reversion.set_user(request.user)
            reversion.set_comment("Création")
        messages.success(request, "Le switch a été créé")
        return redirect("/topologie/")
    i_mbf_param = generate_ipv4_mbf_param(interface, False)
    return form({
        'topoform': switch,
        'machineform': machine,
        'interfaceform': interface,
        'domainform': domain,
        'i_mbf_param': i_mbf_param
        }, 'topologie/switch.html', request)


@login_required
@permission_required('infra')
def create_ports(request, switch_id):
    """ Création d'une liste de ports pour un switch."""
    try:
        switch = Switch.objects.get(pk=switch_id)
    except Switch.DoesNotExist:
        messages.error(request, u"Switch inexistant")
        return redirect("/topologie/")

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
        if end < begin:
            messages.error(request, "Port de fin inférieur au port de début !")
            return redirect("/topologie/switch/" + str(switch.id))
        if end - begin > switch.number:
            messages.error(request, "Ce switch ne peut avoir autant de ports.")
            return redirect("/topologie/switch/" + str(switch.id))

        begin_range = range(begin, s_begin)
        end_range = range(s_end+1, end+1)
        for i in itertools.chain(begin_range, end_range):
            port = Port()
            port.switch = switch
            port.port = i
            try:
                with transaction.atomic(), reversion.create_revision():
                    port.save()
                    reversion.set_user(request.user)
                    reversion.set_comment("Création")
                messages.success(request, "Création du port %d" % i)
            except IntegrityError:
                messages.error(request, "Création d'un port existant.")
        return redirect("/topologie/switch/" + str(switch.id))

    return form({'topoform': port_form}, 'topologie/switch.html', request)


@login_required
@permission_required('infra')
def edit_switch(request, switch_id):
    """ Edition d'un switch. Permet de chambre nombre de ports,
    place dans le stack, interface et machine associée"""
    try:
        switch = Switch.objects.get(pk=switch_id)
    except Switch.DoesNotExist:
        messages.error(request, u"Switch inexistant")
        return redirect("/topologie/")
    switch_form = EditSwitchForm(request.POST or None, instance=switch)
    machine_form = EditMachineForm(
        request.POST or None,
        instance=switch.switch_interface.machine
        )
    interface_form = EditInterfaceForm(
        request.POST or None,
        instance=switch.switch_interface
        )
    domain_form = DomainForm(
        request.POST or None,
        instance=switch.switch_interface.domain
        )
    if switch_form.is_valid() and machine_form.is_valid()\
            and interface_form.is_valid():
        new_interface = interface_form.save(commit=False)
        new_machine = machine_form.save(commit=False)
        new_switch_instance = switch_form.save(commit=False)
        new_domain = domain_form.save(commit=False)
        with transaction.atomic(), reversion.create_revision():
            new_machine.save()
            reversion.set_user(request.user)
            reversion.set_comment(
                "Champs modifié(s) : %s" % ', '.join(
                    field for field in machine_form.changed_data
                    )
                )
        with transaction.atomic(), reversion.create_revision():
            new_interface.save()
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
        with transaction.atomic(), reversion.create_revision():
            new_switch_instance.save()
            reversion.set_user(request.user)
            reversion.set_comment("Champs modifié(s) : %s" % ', '.join(
                field for field in switch_form.changed_data)
                                 )
        messages.success(request, "Le switch a bien été modifié")
        return redirect("/topologie/")
    i_mbf_param = generate_ipv4_mbf_param(interface_form, False)
    return form({
        'topoform': switch_form,
        'machineform': machine_form,
        'interfaceform': interface_form,
        'domainform': domain_form,
        'i_mbf_param': i_mbf_param
        }, 'topologie/switch.html', request)


@login_required
@permission_required('infra')
def new_room(request):
    """Nouvelle chambre """
    room = EditRoomForm(request.POST or None)
    if room.is_valid():
        with transaction.atomic(), reversion.create_revision():
            room.save()
            reversion.set_user(request.user)
            reversion.set_comment("Création")
        messages.success(request, "La chambre a été créé")
        return redirect("/topologie/index_room/")
    return form({'topoform': room}, 'topologie/topo.html', request)


@login_required
@permission_required('infra')
def edit_room(request, room_id):
    """ Edition numero et details de la chambre"""
    try:
        room = Room.objects.get(pk=room_id)
    except Room.DoesNotExist:
        messages.error(request, u"Chambre inexistante")
        return redirect("/topologie/index_room/")
    room = EditRoomForm(request.POST or None, instance=room)
    if room.is_valid():
        with transaction.atomic(), reversion.create_revision():
            room.save()
            reversion.set_user(request.user)
            reversion.set_comment("Champs modifié(s) : %s" % ', '.join(
                field for field in room.changed_data)
                                 )
        messages.success(request, "La chambre a bien été modifiée")
        return redirect("/topologie/index_room/")
    return form({'topoform': room}, 'topologie/topo.html', request)


@login_required
@permission_required('infra')
def del_room(request, room_id):
    """ Suppression d'un chambre"""
    try:
        room = Room.objects.get(pk=room_id)
    except Room.DoesNotExist:
        messages.error(request, u"Chambre inexistante")
        return redirect("/topologie/index_room/")
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
        return redirect("/topologie/index_room/")
    return form({
        'objet': room,
        'objet_name': 'Chambre'
        }, 'topologie/delete.html', request)
