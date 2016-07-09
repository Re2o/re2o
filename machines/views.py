# App de gestion des machines pour re2o
# Gabriel Détraz
# Gplv2
from django.shortcuts import render, redirect
from django.shortcuts import render_to_response, get_object_or_404
from django.core.context_processors import csrf
from django.template import Context, RequestContext, loader
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import ProtectedError

from .forms import NewMachineForm, EditMachineForm, EditInterfaceForm, AddInterfaceForm, NewInterfaceForm, MachineTypeForm, DelMachineTypeForm, ExtensionForm, DelExtensionForm
from .models import Machine, Interface, IpList, MachineType, Extension
from users.models import User

def unassign_ips(user):
    machines = Interface.objects.filter(machine=Machine.objects.filter(user=user))
    for machine in machines:
        unassign_ipv4(machine)
    return

def assign_ips(user):
    """ Assign une ipv4 aux machines d'un user """
    machines = Interface.objects.filter(machine=Machine.objects.filter(user=user))
    for machine in machines:
        if not machine.ipv4:
            interface = assign_ipv4(machine)
            interface.save()
    return

def free_ip():
    """ Renvoie la liste des ip disponibles """
    return IpList.objects.filter(interface__isnull=True)

def assign_ipv4(interface):
    """ Assigne une ip à l'interface """
    free_ips = free_ip()
    if free_ips:
        interface.ipv4 = free_ips[0]
    return interface

def unassign_ipv4(interface):
    interface.ipv4 = None
    interface.save()

def form(ctx, template, request):
    c = ctx
    c.update(csrf(request))
    return render_to_response(template, c, context_instance=RequestContext(request))

@login_required
def new_machine(request, userid):
    try:
        user = User.objects.get(pk=userid)
    except User.DoesNotExist:
        messages.error(request, u"Utilisateur inexistant" )
        return redirect("/machines/")
    machine = NewMachineForm(request.POST or None)
    interface = AddInterfaceForm(request.POST or None) 
    if machine.is_valid() and interface.is_valid():
        new_machine = machine.save(commit=False)
        new_machine.user = user
        new_machine.save()
        new_interface = interface.save(commit=False)
        new_interface.machine = new_machine
        if free_ip() and not new_interface.ipv4:
            new_interface = assign_ipv4(new_interface)
        elif not new_interface.ipv4:
            messages.error(request, u"Il n'y a plus d'ip disponibles")
        new_interface.save()
        messages.success(request, "La machine a été crée")
        return redirect("/users/profil/" + userid)
    return form({'machineform': machine, 'interfaceform': interface}, 'machines/machine.html', request)

@login_required
def edit_machine(request, interfaceid):
    try:
        interface = Interface.objects.get(pk=interfaceid)
    except Interface.DoesNotExist:
        messages.error(request, u"Interface inexistante" )
        return redirect("/machines")
    machine_form = EditMachineForm(request.POST or None, instance=interface.machine)
    interface_form = EditInterfaceForm(request.POST or None, instance=interface)
    if machine_form.is_valid() and interface_form.is_valid():
        machine_form.save()
        interface_form.save()
        messages.success(request, "La machine a été modifiée")
        return redirect("/machines/")
    return form({'machineform': machine_form, 'interfaceform': interface_form}, 'machines/machine.html', request)

@login_required
def new_interface(request, machineid):
    try:
        machine = Machine.objects.get(pk=machineid)
    except Machine.DoesNotExist:
        messages.error(request, u"Machine inexistante" )
        return redirect("/machines")
    interface_form = AddInterfaceForm(request.POST or None)
    machine_form = EditMachineForm(request.POST or None, instance=machine)
    if interface_form.is_valid() and machine_form.is_valid():
        machine_form.save()
        new_interface = interface_form.save(commit=False)
        new_interface.machine = machine
        if free_ip() and not new_interface.ipv4:
            new_interface = assign_ipv4(new_interface)
        elif not new_interface.ipv4:
            messages.error(request, u"Il n'y a plus d'ip disponibles")
        new_interface.save()
        messages.success(request, "L'interface a été ajoutée")
        return redirect("/machines/")
    return form({'machineform': machine_form, 'interfaceform': interface_form}, 'machines/machine.html', request)

@login_required
@permission_required('admin')
def add_machinetype(request):
    machinetype = MachineTypeForm(request.POST or None)
    if machinetype.is_valid():
        machinetype.save()
        messages.success(request, "Ce type de machine a été ajouté")
        return redirect("/machines/index_machinetype")
    return form({'machineform': machinetype, 'interfaceform': None}, 'machines/machine.html', request)

@login_required
@permission_required('admin')
def edit_machinetype(request, machinetypeid):
    try:
        machinetype_instance = MachineType.objects.get(pk=machinetypeid)
    except MachineType.DoesNotExist:
        messages.error(request, u"Entrée inexistante" )
        return redirect("/machines/index_machinetype/")
    machinetype = MachineTypeForm(request.POST or None, instance=machinetype_instance)
    if machinetype.is_valid():
        machinetype.save()
        messages.success(request, "Type de machine modifié")
        return redirect("/machines/index_machinetype/")
    return form({'machineform': machinetype}, 'machines/machine.html', request)

@login_required
@permission_required('admin')
def del_machinetype(request):
    machinetype = DelMachineTypeForm(request.POST or None)
    if machinetype.is_valid():
        machinetype_dels = machinetype.cleaned_data['machinetypes']
        for machinetype_del in machinetype_dels:
            try:
                machinetype_del.delete()
                messages.success(request, "Le type de machine a été supprimé")
            except ProtectedError:
                messages.error(request, "Le type de machine %s est affectée à au moins une machine, vous ne pouvez pas le supprimer" % machinetype_del)
        return redirect("/machines/index_machinetype")
    return form({'machineform': machinetype, 'interfaceform': None}, 'machines/machine.html', request)

@login_required
@permission_required('admin')
def add_extension(request):
    extension = ExtensionForm(request.POST or None)
    if extension.is_valid():
        extension.save()
        messages.success(request, "Cette extension a été ajoutée")
        return redirect("/machines/index_extension")
    return form({'machineform': extension, 'interfaceform': None}, 'machines/machine.html', request)

@login_required
@permission_required('admin')
def edit_extension(request, extensionid):
    try:
        extension_instance = Extension.objects.get(pk=extensionid)
    except Extension.DoesNotExist:
        messages.error(request, u"Entrée inexistante" )
        return redirect("/machines/index_extension/")
    extension = ExtensionForm(request.POST or None, instance=extension_instance)
    if extension.is_valid():
        extension.save()
        messages.success(request, "Extension modifiée")
        return redirect("/machines/index_extension/")
    return form({'machineform': extension}, 'machines/machine.html', request)

@login_required
@permission_required('admin')
def del_extension(request):
    extension = DelExtensionForm(request.POST or None)
    if extension.is_valid():
        extension_dels = extension.cleaned_data['extensions']
        for extension_del in extension_dels:
            try:
                extension_del.delete()
                messages.success(request, "L'extension a été supprimée")
            except ProtectedError:
                messages.error(request, "L'extension %s est affectée à au moins un type de machine, vous ne pouvez pas la supprimer" % extension_del)
        return redirect("/machines/index_extension")
    return form({'machineform': extension, 'interfaceform': None}, 'machines/machine.html', request)

@login_required
def index(request):
    interfaces_list = Interface.objects.order_by('pk')
    return render(request, 'machines/index.html', {'interfaces_list': interfaces_list})

@login_required
def index_machinetype(request):
    is_admin = request.user.has_perms(('admin',))
    machinetype_list = MachineType.objects.order_by('type')
    return render(request, 'machines/index_machinetype.html', {'machinetype_list':machinetype_list, 'is_admin':is_admin})

@login_required
def index_extension(request):
    is_admin = request.user.has_perms(('admin',))
    extension_list = Extension.objects.order_by('name')
    return render(request, 'machines/index_extension.html', {'extension_list':extension_list, 'is_admin':is_admin})
