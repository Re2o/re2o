# App de gestion des machines pour re2o
# Gabriel Détraz, Augustin Lemesle
# Gplv2
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.shortcuts import render_to_response, get_object_or_404
from django.core.context_processors import csrf
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.template import Context, RequestContext, loader
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import ProtectedError
from django.forms import ValidationError
from django.db import transaction
from django.contrib.auth import authenticate, login
from django.views.decorators.csrf import csrf_exempt

from rest_framework.renderers import JSONRenderer
from machines.serializers import InterfaceSerializer, TypeSerializer, AliasSerializer
from reversion import revisions as reversion


import re
from .forms import NewMachineForm, EditMachineForm, EditInterfaceForm, AddInterfaceForm, MachineTypeForm, DelMachineTypeForm, ExtensionForm, DelExtensionForm, BaseEditInterfaceForm, BaseEditMachineForm, Alias
from .forms import IpTypeForm, DelIpTypeForm, NewAliasForm, EditAliasForm, MxForm, DelMxForm
from .models import IpType, Machine, Interface, IpList, MachineType, Extension, Mx, Ns
from users.models import User
from re2o.settings import PAGINATION_NUMBER, PAGINATION_LARGE_NUMBER

def full_domain_validator(request, interface):
    """ Validation du nom de domaine, extensions dans type de machine, prefixe pas plus long que 63 caractères """
    HOSTNAME_LABEL_PATTERN = re.compile("(?!-)[A-Z\d-]+(?<!-)$", re.IGNORECASE)
    dns = interface.dns.lower()
    if len(dns) > 63:
        messages.error(request,
                "Le nom de domaine %s est trop long (maximum de 63 caractères)." % dns)
        return False
    if not HOSTNAME_LABEL_PATTERN.match(dns):
        messages.error(request,
                "Ce nom de domaine %s contient des carractères interdits." % dns)
        return False
    return True

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
            with transaction.atomic(), reversion.create_revision():
                reversion.set_comment("Assignation ipv4")
                interface.save()
    return

def free_ip(type):
    """ Renvoie la liste des ip disponibles """
    return IpList.objects.filter(interface__isnull=True).filter(ip_type=type)

def assign_ipv4(interface):
    """ Assigne une ip à l'interface """
    free_ips = free_ip(interface.type.ip_type)
    if free_ips:
        interface.ipv4 = free_ips[0]
    return interface

def unassign_ipv4(interface):
    interface.ipv4 = None
    with transaction.atomic(), reversion.create_revision():
        reversion.set_comment("Désassignation ipv4")
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
    if not request.user.has_perms(('cableur',)) and user != request.user:
        messages.error(request, "Vous ne pouvez pas ajouter une machine à un autre user que vous sans droit")
        return redirect("/users/profil/" + str(request.user.id))
    machine = NewMachineForm(request.POST or None)
    interface = AddInterfaceForm(request.POST or None, infra=request.user.has_perms(('infra',))) 
    if machine.is_valid() and interface.is_valid():
        new_machine = machine.save(commit=False)
        new_machine.user = user
        new_interface = interface.save(commit=False)
        if full_domain_validator(request, new_interface):
            with transaction.atomic(), reversion.create_revision():
                new_machine.save()
                reversion.set_user(request.user)
                reversion.set_comment("Création")
            new_interface.machine = new_machine
            if free_ip(new_interface.type.ip_type) and not new_interface.ipv4:
                new_interface = assign_ipv4(new_interface)
            elif not new_interface.ipv4:
                messages.error(request, u"Il n'y a plus d'ip disponibles")
            with transaction.atomic(), reversion.create_revision():
                new_interface.save()
                reversion.set_user(request.user)
                reversion.set_comment("Création")
            messages.success(request, "La machine a été crée")
            return redirect("/users/profil/" + userid)
    return form({'machineform': machine, 'interfaceform': interface}, 'machines/machine.html', request)

@login_required
def edit_interface(request, interfaceid):
    try:
        interface = Interface.objects.get(pk=interfaceid)
    except Interface.DoesNotExist:
        messages.error(request, u"Interface inexistante" )
        return redirect("/machines")
    if not request.user.has_perms(('infra',)):
        if not request.user.has_perms(('cableur',)) and interface.machine.user != request.user:
            messages.error(request, "Vous ne pouvez pas éditer une machine d'un autre user que vous sans droit")
            return redirect("/users/profil/" + str(request.user.id))
        machine_form = BaseEditMachineForm(request.POST or None, instance=interface.machine)
        interface_form = BaseEditInterfaceForm(request.POST or None, instance=interface, infra=False)
    else:
        machine_form = EditMachineForm(request.POST or None, instance=interface.machine)
        interface_form = EditInterfaceForm(request.POST or None, instance=interface)
    if machine_form.is_valid() and interface_form.is_valid():
        new_interface = interface_form.save(commit=False)
        new_machine = machine_form.save(commit=False)
        if full_domain_validator(request, new_interface):
            with transaction.atomic(), reversion.create_revision():
                new_machine.save()
                reversion.set_user(request.user)
                reversion.set_comment("Champs modifié(s) : %s" % ', '.join(field for field in machine_form.changed_data))
            with transaction.atomic(), reversion.create_revision():
                new_interface.save()
                reversion.set_user(request.user)
                reversion.set_comment("Champs modifié(s) : %s" % ', '.join(field for field in interface_form.changed_data))
            messages.success(request, "La machine a été modifiée")
            return redirect("/users/profil/" + str(interface.machine.user.id))
    return form({'machineform': machine_form, 'interfaceform': interface_form}, 'machines/machine.html', request)

@login_required
def manage_alias(request, interfaceid):
    try:
        interface = Interface.objects.get(pk=interfaceid)
    except Interface.DoesNotExist:
        messages.error(request, u"Interface inexistante" )
        return redirect("/machines")
    if not request.user.has_perms(('infra',)):
        if not request.user.has_perms(('cableur',)) and interface.machine.user != request.user:
            messages.error(request, "Vous ne pouvez pas éditer une machine d'un autre user que vous sans droit")
            return redirect("/users/profil/" + str(request.user.id))


@login_required
def del_machine(request, machineid):
    try:
        machine = Machine.objects.get(pk=machineid)
    except Machine.DoesNotExist:
        messages.error(request, u"Machine inexistante" )
        return redirect("/machines")
    if not request.user.has_perms(('cableur',)):
        if machine.user != request.user:
            messages.error(request, "Vous ne pouvez pas éditer une machine d'un autre user que vous sans droit")
            return redirect("/users/profil/" + str(request.user.id))
    if request.method == "POST":
        with transaction.atomic(), reversion.create_revision():
            machine.delete()
            reversion.set_user(request.user)
        messages.success(request, "La machine a été détruite")
        return redirect("/users/profil/" + str(request.user.id))
    return form({'objet': machine, 'objet_name': 'machine'}, 'machines/delete.html', request)

@login_required
def new_interface(request, machineid):
    try:
        machine = Machine.objects.get(pk=machineid)
    except Machine.DoesNotExist:
        messages.error(request, u"Machine inexistante" )
        return redirect("/machines")
    if not request.user.has_perms(('cableur',)):
        if machine.user != request.user:
            messages.error(request, "Vous ne pouvez pas ajouter une interface à une machine d'un autre user que vous sans droit")
            return redirect("/users/profil/" + str(request.user.id))
    interface_form = AddInterfaceForm(request.POST or None, infra=request.user.has_perms(('infra',)))
    if interface_form.is_valid():
        new_interface = interface_form.save(commit=False)
        new_interface.machine = machine
        if full_domain_validator(request, new_interface):
            if free_ip(new_interface.type.ip_type) and not new_interface.ipv4:
                new_interface = assign_ipv4(new_interface)
            elif not new_interface.ipv4:
                messages.error(request, u"Il n'y a plus d'ip disponibles")
            with transaction.atomic(), reversion.create_revision():
                new_interface.save()
                reversion.set_user(request.user)
                reversion.set_comment("Création")
            messages.success(request, "L'interface a été ajoutée")
            return redirect("/users/profil/" + str(request.user.id))
    return form({'interfaceform': interface_form}, 'machines/machine.html', request)

@login_required
def del_interface(request, interfaceid):
    try:
        interface = Interface.objects.get(pk=interfaceid)
    except Interface.DoesNotExist:
        messages.error(request, u"Interface inexistante" )
        return redirect("/machines")
    if not request.user.has_perms(('cableur',)):
        if interface.machine.user != request.user:
            messages.error(request, "Vous ne pouvez pas éditer une machine d'un autre user que vous sans droit")
            return redirect("/users/profil/" + str(request.user.id))
    if request.method == "POST":
        with transaction.atomic(), reversion.create_revision():
            interface.delete()
            reversion.set_user(request.user)
        messages.success(request, "L'interface a été détruite")
        return redirect("/users/profil/" + str(request.user.id))
    return form({'objet': interface, 'objet_name': 'interface'}, 'machines/delete.html', request)

@login_required
@permission_required('infra')
def add_iptype(request):
    iptype = IpTypeForm(request.POST or None)
    if iptype.is_valid():
        with transaction.atomic(), reversion.create_revision():
            iptype.save()
            reversion.set_user(request.user)
            reversion.set_comment("Création")
        messages.success(request, "Ce type d'ip a été ajouté")
        return redirect("/machines/index_iptype")
    return form({'machineform': iptype, 'interfaceform': None}, 'machines/machine.html', request)

@login_required
@permission_required('infra')
def edit_iptype(request, iptypeid):
    try:
        iptype_instance = IpType.objects.get(pk=iptypeid)
    except IpType.DoesNotExist:
        messages.error(request, u"Entrée inexistante" )
        return redirect("/machines/index_iptype/")
    iptype = IpTypeForm(request.POST or None, instance=iptype_instance)
    if iptype.is_valid():
        with transaction.atomic(), reversion.create_revision():
            iptype.save()
            reversion.set_user(request.user)
            reversion.set_comment("Champs modifié(s) : %s" % ', '.join(field for field in iptype.changed_data))
        messages.success(request, "Type d'ip modifié")
        return redirect("/machines/index_iptype/")
    return form({'machineform': iptype}, 'machines/machine.html', request)

@login_required
@permission_required('infra')
def del_iptype(request):
    iptype = DelIpTypeForm(request.POST or None)
    if iptype.is_valid():
        iptype_dels = iptype.cleaned_data['iptypes']
        for iptype_del in iptype_dels:
            try:
                with transaction.atomic(), reversion.create_revision():
                    iptype_del.delete()
                    reversion.set_user(request.user)
                messages.success(request, "Le type d'ip a été supprimé")
            except ProtectedError:
                messages.error(request, "Le type d'ip %s est affectée à au moins une machine, vous ne pouvez pas le supprimer" % iptype_del)
        return redirect("/machines/index_iptype")
    return form({'machineform': iptype, 'interfaceform': None}, 'machines/machine.html', request)

@login_required
@permission_required('infra')
def add_machinetype(request):
    machinetype = MachineTypeForm(request.POST or None)
    if machinetype.is_valid():
        with transaction.atomic(), reversion.create_revision():
            machinetype.save()
            reversion.set_user(request.user)
            reversion.set_comment("Création")
        messages.success(request, "Ce type de machine a été ajouté")
        return redirect("/machines/index_machinetype")
    return form({'machineform': machinetype, 'interfaceform': None}, 'machines/machine.html', request)

@login_required
@permission_required('infra')
def edit_machinetype(request, machinetypeid):
    try:
        machinetype_instance = MachineType.objects.get(pk=machinetypeid)
    except MachineType.DoesNotExist:
        messages.error(request, u"Entrée inexistante" )
        return redirect("/machines/index_machinetype/")
    machinetype = MachineTypeForm(request.POST or None, instance=machinetype_instance)
    if machinetype.is_valid():
        with transaction.atomic(), reversion.create_revision():
            machinetype.save()
            reversion.set_user(request.user)
            reversion.set_comment("Champs modifié(s) : %s" % ', '.join(field for field in machinetype.changed_data))
        messages.success(request, "Type de machine modifié")
        return redirect("/machines/index_machinetype/")
    return form({'machineform': machinetype}, 'machines/machine.html', request)

@login_required
@permission_required('infra')
def del_machinetype(request):
    machinetype = DelMachineTypeForm(request.POST or None)
    if machinetype.is_valid():
        machinetype_dels = machinetype.cleaned_data['machinetypes']
        for machinetype_del in machinetype_dels:
            try:
                with transaction.atomic(), reversion.create_revision():
                    machinetype_del.delete()
                    reversion.set_user(request.user)
                messages.success(request, "Le type de machine a été supprimé")
            except ProtectedError:
                messages.error(request, "Le type de machine %s est affectée à au moins une machine, vous ne pouvez pas le supprimer" % machinetype_del)
        return redirect("/machines/index_machinetype")
    return form({'machineform': machinetype, 'interfaceform': None}, 'machines/machine.html', request)

@login_required
@permission_required('infra')
def add_extension(request):
    extension = ExtensionForm(request.POST or None)
    if extension.is_valid():
        with transaction.atomic(), reversion.create_revision():
            extension.save()
            reversion.set_user(request.user)
            reversion.set_comment("Création")
        messages.success(request, "Cette extension a été ajoutée")
        return redirect("/machines/index_extension")
    return form({'machineform': extension, 'interfaceform': None}, 'machines/machine.html', request)

@login_required
@permission_required('infra')
def edit_extension(request, extensionid):
    try:
        extension_instance = Extension.objects.get(pk=extensionid)
    except Extension.DoesNotExist:
        messages.error(request, u"Entrée inexistante" )
        return redirect("/machines/index_extension/")
    extension = ExtensionForm(request.POST or None, instance=extension_instance)
    if extension.is_valid():
        with transaction.atomic(), reversion.create_revision():
            extension.save()
            reversion.set_user(request.user)
            reversion.set_comment("Champs modifié(s) : %s" % ', '.join(field for field in extension.changed_data))
        messages.success(request, "Extension modifiée")
        return redirect("/machines/index_extension/")
    return form({'machineform': extension}, 'machines/machine.html', request)

@login_required
@permission_required('infra')
def del_extension(request):
    extension = DelExtensionForm(request.POST or None)
    if extension.is_valid():
        extension_dels = extension.cleaned_data['extensions']
        for extension_del in extension_dels:
            try:
                with transaction.atomic(), reversion.create_revision():
                    extension_del.delete()
                    reversion.set_user(request.user)
                messages.success(request, "L'extension a été supprimée")
            except ProtectedError:
                messages.error(request, "L'extension %s est affectée à au moins un type de machine, vous ne pouvez pas la supprimer" % extension_del)
        return redirect("/machines/index_extension")
    return form({'machineform': extension, 'interfaceform': None}, 'machines/machine.html', request)

@login_required
@permission_required('infra')
def add_mx(request):
    mx = MxForm(request.POST or None)
    if mx.is_valid():
        with transaction.atomic(), reversion.create_revision():
            mx.save()
            reversion.set_user(request.user)
            reversion.set_comment("Création")
        messages.success(request, "Cet enregistrement mx a été ajouté")
        return redirect("/machines/index_extension")
    return form({'machineform': mx, 'interfaceform': None}, 'machines/machine.html', request)

@login_required
@permission_required('infra')
def edit_mx(request, mxid):
    try:
        mx_instance = Mx.objects.get(pk=mxid)
    except Mx.DoesNotExist:
        messages.error(request, u"Entrée inexistante" )
        return redirect("/machines/index_extension/")
    mx = MxForm(request.POST or None, instance=mx_instance)
    if mx.is_valid():
        with transaction.atomic(), reversion.create_revision():
            mx.save()
            reversion.set_user(request.user)
            reversion.set_comment("Champs modifié(s) : %s" % ', '.join(field for field in mx.changed_data))
        messages.success(request, "Mx modifié")
        return redirect("/machines/index_extension/")
    return form({'machineform': mx}, 'machines/machine.html', request)

@login_required
@permission_required('infra')
def del_mx(request):
    mx = DelMxForm(request.POST or None)
    if mx.is_valid():
        mx_dels = mx.cleaned_data['mx']
        for mx_del in mx_dels:
            try:
                with transaction.atomic(), reversion.create_revision():
                    mx_del.delete()
                    reversion.set_user(request.user)
                messages.success(request, "L'mx a été supprimée")
            except ProtectedError:
                messages.error(request, "Erreur le Mx suivant %s ne peut être supprimé" % mx_del)
        return redirect("/machines/index_extension")
    return form({'machineform': mx, 'interfaceform': None}, 'machines/machine.html', request)

@login_required
@permission_required('cableur')
def index(request):
    machines_list = Machine.objects.order_by('pk')
    paginator = Paginator(machines_list, PAGINATION_LARGE_NUMBER)
    page = request.GET.get('page')
    try:
        machines_list = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        machines_list = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        machines_list = paginator.page(paginator.num_pages)
    return render(request, 'machines/index.html', {'machines_list': machines_list})

@login_required
@permission_required('cableur')
def index_iptype(request):
    iptype_list = IpType.objects.order_by('type')
    return render(request, 'machines/index_iptype.html', {'iptype_list':iptype_list})

@login_required
@permission_required('cableur')
def index_machinetype(request):
    machinetype_list = MachineType.objects.order_by('type')
    return render(request, 'machines/index_machinetype.html', {'machinetype_list':machinetype_list})

@login_required
@permission_required('cableur')
def index_extension(request):
    extension_list = Extension.objects.order_by('name')
    mx_list = Mx.objects.order_by('zone')
    ns_list = Ns.objects.order_by('zone')
    return render(request, 'machines/index_extension.html', {'extension_list':extension_list, 'mx_list': mx_list, 'ns_list': ns_list})

@login_required
def history(request, object, id):
    if object == 'machine':
        try:
             object_instance = Machine.objects.get(pk=id)
        except Machine.DoesNotExist:
             messages.error(request, "Machine inexistante")
             return redirect("/machines/")
        if not request.user.has_perms(('cableur',)) and object_instance.user != request.user:
             messages.error(request, "Vous ne pouvez pas afficher l'historique d'une machine d'un autre user que vous sans droit cableur")
             return redirect("/users/profil/" + str(request.user.id))
    elif object == 'interface':
        try:
             object_instance = Interface.objects.get(pk=id)
        except Interface.DoesNotExist:
             messages.error(request, "Interface inexistante")
             return redirect("/machines/")
        if not request.user.has_perms(('cableur',)) and object_instance.machine.user != request.user:
             messages.error(request, "Vous ne pouvez pas afficher l'historique d'une interface d'un autre user que vous sans droit cableur")
             return redirect("/users/profil/" + str(request.user.id))
    elif object == 'machinetype' and request.user.has_perms(('cableur',)):
        try:
             object_instance = MachineType.objects.get(pk=id)
        except MachineType.DoesNotExist:
             messages.error(request, "Type de machine inexistant")
             return redirect("/machines/")
    elif object == 'iptype' and request.user.has_perms(('cableur',)):
        try:
             object_instance = IpType.objects.get(pk=id)
        except IpType.DoesNotExist:
             messages.error(request, "Type d'ip inexistant")
             return redirect("/machines/")
    elif object == 'extension' and request.user.has_perms(('cableur',)):
        try:
             object_instance = Extension.objects.get(pk=id)
        except Extension.DoesNotExist:
             messages.error(request, "Extension inexistante")
             return redirect("/machines/")
    elif object == 'mx' and request.user.has_perms(('cableur',)):
        try:
             object_instance = Mx.objects.get(pk=id)
        except Mx.DoesNotExist:
             messages.error(request, "Mx inexistant")
             return redirect("/machines/")
    else:
        messages.error(request, "Objet  inconnu")
        return redirect("/machines/")
    reversions = reversion.get_for_object(object_instance)
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


""" Framework Rest """

class JSONResponse(HttpResponse):
    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)

@csrf_exempt
@login_required
@permission_required('serveur')
def interface_list(request):
    interfaces = Interface.objects.all()
    interface = []
    for i in interfaces :
        if i.ipv4 and i.is_active():
            interface.append(i)
    seria = InterfaceSerializer(interface, many=True) 
    return seria.data

@csrf_exempt
@login_required
@permission_required('serveur')
def alias(request):
    alias = Alias.objects.all()
    seria = AliasSerializer(alias, many=True)
    for d in seria.data:
        if d["interface_parent"]["ipv4"]:
            id = d["interface_parent"]["ipv4"]
            ip_list = IpList.objects.get(pk=id)
            d["interface_parent"]["extension"] = ip_list.ip_type.extension.name
            d["interface_parent"].pop("ipv4")
    return JSONResponse(seria.data)

@csrf_exempt
@login_required
@permission_required('serveur')
def corresp(request):
    type = IpType.objects.all()
    seria = TypeSerializer(type, many=True)
    return JSONResponse(seria.data)

@csrf_exempt
@login_required
@permission_required('serveur')
def mac_ip(request):
    seria = interface_list(request)
    for s in seria:
        s.pop('dns')
    return JSONResponse(seria)

@csrf_exempt
@login_required
@permission_required('serveur')
def mac_ip_dns(request):
    seria = interface_list(request)
    return JSONResponse(seria)

@csrf_exempt
def login_user(request):
    user = authenticate(username=request.POST['username'], password=request.POST['password'])
    login(request, user)
    return HttpResponse("Logged In")
