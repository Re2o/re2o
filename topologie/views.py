from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.db import IntegrityError
from django.db import transaction
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from reversion import revisions as reversion
from reversion.models import Version

from topologie.models import Switch, Port, Room
from topologie.forms import EditPortForm, NewSwitchForm, EditSwitchForm, AddPortForm, EditRoomForm
from users.views import form
from users.models import User

from machines.forms import NewMachineForm, EditMachineForm, EditInterfaceForm, AddInterfaceForm
from machines.views import free_ip, full_domain_validator, assign_ipv4

from re2o.settings import ASSO_PSEUDO, PAGINATION_NUMBER

@login_required
@permission_required('cableur')
def index(request):
    switch_list = Switch.objects.order_by('location')
    return render(request, 'topologie/index.html', {'switch_list': switch_list})

@login_required
@permission_required('cableur')
def history(request, object, id):
    if object == 'switch':
        try:
             object_instance = Switch.objects.get(pk=id)
        except Switch.DoesNotExist:
             messages.error(request, "Switch inexistant")
             return redirect("/topologie/")
    elif object == 'port':
        try:
             object_instance = Port.objects.get(pk=id)
        except Port.DoesNotExist:
             messages.error(request, "Port inexistant")
             return redirect("/topologie/") 
    elif object == 'room':  
        try:
             object_instance = Room.objects.get(pk=id)
        except Room.DoesNotExist:
             messages.error(request, "Chambre inexistante")
             return redirect("/topologie/")
    else:
        messages.error(request, "Objet  inconnu")
        return redirect("/topologie/")
    reversions = Version.objects.get_for_object(object_instance)
    paginator = Paginator(reversions, PAGINATION_NUMBER)
    page = request.GET.get('page')
    try:
        reversions = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        reversions = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        reversions = paginator.page(paginator.num_pages)
    return render(request, 're2o/history.html', {'reversions': reversions, 'object': object_instance})

@login_required
@permission_required('cableur')
def index_port(request, switch_id):
    try:
        switch = Switch.objects.get(pk=switch_id)
    except Switch.DoesNotExist:
        messages.error(request, u"Switch inexistant")
        return redirect("/topologie/")
    port_list = Port.objects.filter(switch = switch).order_by('port')
    return render(request, 'topologie/index_p.html', {'port_list':port_list, 'id_switch':switch_id, 'nom_switch':switch})

@login_required
@permission_required('cableur')
def index_room(request):
    room_list = Room.objects.order_by('name')
    return render(request, 'topologie/index_room.html', {'room_list': room_list})

@login_required
@permission_required('infra')
def new_port(request, switch_id):
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
            messages.error(request,"Ce port existe déjà" )
        return redirect("/topologie/switch/" + switch_id)
    return form({'topoform':port}, 'topologie/topo.html', request)

@login_required
@permission_required('infra')
def edit_port(request, port_id):
    try:
        port_object = Port.objects.get(pk=port_id)
    except Port.DoesNotExist:
        messages.error(request, u"Port inexistant")
        return redirect("/topologie/")
    port = EditPortForm(request.POST or None, instance=port_object)
    if port.is_valid():
        with transaction.atomic(), reversion.create_revision():
            port.save()
            reversion.set_user(request.user)
            reversion.set_comment("Champs modifié(s) : %s" % ', '.join(field for field in port.changed_data))
        messages.success(request, "Le port a bien été modifié")
        return redirect("/topologie/switch/" + str(port_object.switch.id))
    return form({'topoform':port}, 'topologie/topo.html', request)

@login_required
@permission_required('infra')
def new_switch(request):
    switch = NewSwitchForm(request.POST or None)
    machine = NewMachineForm(request.POST or None)
    interface = AddInterfaceForm(request.POST or None, infra=request.user.has_perms(('infra',)))
    if switch.is_valid() and machine.is_valid() and interface.is_valid():
        try:
            user = User.objects.get(pseudo=ASSO_PSEUDO)
        except User.DoesNotExist:
            messages.error(request, "L'user %s n'existe pas encore, veuillez le créer" % ASSO_PSEUDO)
            return redirect("/topologie/")
        new_machine = machine.save(commit=False)
        new_machine.user = user
        new_interface = interface.save(commit=False)
        new_switch = switch.save(commit=False)
        if full_domain_validator(request, new_interface):
            with transaction.atomic(), reversion.create_revision():
                new_machine.save()
                reversion.set_user(request.user)
                reversion.set_comment("Création")
            new_interface.machine = new_machine
            if free_ip(new_interface.type.ip_type) and not new_interface.ipv4:
                new_interface = assign_ipv4(new_interface)
            elif not new_interface.ipv4:
                messages.error(request, "Il n'y a plus d'ip disponibles")
            with transaction.atomic(), reversion.create_revision():
                new_interface.save()
                reversion.set_user(request.user)
                reversion.set_comment("Création")
            new_switch.switch_interface = new_interface
            with transaction.atomic(), reversion.create_revision():
                new_switch.save()
                reversion.set_user(request.user)
                reversion.set_comment("Création")
            messages.success(request, "Le switch a été crée")
            return redirect("/topologie/")
    return form({'topoform':switch, 'machineform': machine, 'interfaceform': interface}, 'topologie/switch.html', request)

@login_required
@permission_required('infra')
def edit_switch(request, switch_id):
    try:
        switch = Switch.objects.get(pk=switch_id)
    except Switch.DoesNotExist:
        messages.error(request, u"Switch inexistant")
        return redirect("/topologie/")
    switch_form = EditSwitchForm(request.POST or None, instance=switch)
    machine_form = EditMachineForm(request.POST or None, instance=switch.switch_interface.machine)
    interface_form = EditInterfaceForm(request.POST or None, instance=switch.switch_interface)
    if switch_form.is_valid() and machine_form.is_valid() and interface_form.is_valid():
        new_interface = interface_form.save(commit=False)
        new_machine = machine_form.save(commit=False)
        new_switch = switch_form.save(commit=False)
        if full_domain_validator(request, new_interface):
            with transaction.atomic(), reversion.create_revision():
                new_machine.save()
                reversion.set_user(request.user)
                reversion.set_comment("Champs modifié(s) : %s" % ', '.join(field for field in machine_form.changed_data))
            with transaction.atomic(), reversion.create_revision():
                new_interface.save()
                reversion.set_user(request.user)
                reversion.set_comment("Champs modifié(s) : %s" % ', '.join(field for field in interface_form.changed_data))
            with transaction.atomic(), reversion.create_revision():
                new_switch.save()
                reversion.set_user(request.user)
                reversion.set_comment("Champs modifié(s) : %s" % ', '.join(field for field in switch_form.changed_data))
            messages.success(request, "Le switch a bien été modifié")
            return redirect("/topologie/")
    return form({'topoform':switch_form, 'machineform': machine_form, 'interfaceform': interface_form}, 'topologie/switch.html', request)

@login_required
@permission_required('infra')
def new_room(request):
    room = EditRoomForm(request.POST or None)
    if room.is_valid():
        with transaction.atomic(), reversion.create_revision():
            room.save()
            reversion.set_user(request.user)
            reversion.set_comment("Création")
        messages.success(request, "La chambre a été créé")
        return redirect("/topologie/index_room/")
    return form({'topoform':room}, 'topologie/topo.html', request)

@login_required
@permission_required('infra')
def edit_room(request, room_id):
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
            reversion.set_comment("Champs modifié(s) : %s" % ', '.join(field for field in room.changed_data))
        messages.success(request, "La chambre a bien été modifiée")
        return redirect("/topologie/index_room/")
    return form({'topoform':room}, 'topologie/topo.html', request)

@login_required
@permission_required('infra')
def del_room(request, room_id):
    try:
        room = Room.objects.get(pk=room_id)
    except Room.DoesNotExist:
        messages.error(request, u"Chambre inexistante" )
        return redirect("/topologie/index_room/")
    if request.method == "POST":
        with transaction.atomic(), reversion.create_revision():
            room.delete()
            reversion.set_user(request.user)
            reversion.set_comment("Destruction")
        messages.success(request, "La chambre/prise a été détruite")
        return redirect("/topologie/index_room/")
    return form({'objet': room, 'objet_name': 'Chambre'}, 'topologie/delete.html', request)
