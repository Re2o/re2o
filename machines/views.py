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

# App de gestion des machines pour re2o
# Gabriel Détraz, Augustin Lemesle
# Gplv2
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404
from django.template.context_processors import csrf
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
from machines.serializers import InterfaceSerializer, TypeSerializer, DomainSerializer, MxSerializer, ExtensionSerializer, NsSerializer
from reversion import revisions as reversion
from reversion.models import Version

import re
from .forms import NewMachineForm, EditMachineForm, EditInterfaceForm, AddInterfaceForm, MachineTypeForm, DelMachineTypeForm, ExtensionForm, DelExtensionForm, BaseEditInterfaceForm, BaseEditMachineForm
from .forms import IpTypeForm, DelIpTypeForm, AliasForm, DelAliasForm, NsForm, DelNsForm, MxForm, DelMxForm
from .models import IpType, Machine, Interface, IpList, MachineType, Extension, Mx, Ns, Domain
from users.models import User
from users.models import all_has_access
from re2o.settings import PAGINATION_NUMBER, PAGINATION_LARGE_NUMBER, MAX_INTERFACES, MAX_ALIAS

def full_domain_validator(request, domain):
    """ Validation du nom de domaine, extensions dans type de machine, prefixe pas plus long que 63 caractères """
    HOSTNAME_LABEL_PATTERN = re.compile("(?!-)[A-Z\d-]+(?<!-)$", re.IGNORECASE)
    dns = domain.name.lower()
    if len(dns) > 63:
        messages.error(request,
                "Le nom de domaine %s est trop long (maximum de 63 caractères)." % dns)
        return False
    if not HOSTNAME_LABEL_PATTERN.match(dns):
        messages.error(request,
                "Ce nom de domaine %s contient des carractères interdits." % dns)
        return False
    return True

def all_active_interfaces():
    """Renvoie l'ensemble des machines autorisées à sortir sur internet """
    return Interface.objects.filter(machine__in=Machine.objects.filter(user__in=all_has_access()).filter(active=True)).select_related('domain').select_related('machine').select_related('type').select_related('ipv4').select_related('domain__extension').select_related('ipv4__ip_type').distinct()

def all_active_assigned_interfaces():
    """ Renvoie l'ensemble des machines qui ont une ipv4 assignées et disposant de l'accès internet"""
    return all_active_interfaces().filter(ipv4__isnull=False)

def all_active_interfaces_count():
    """ Version light seulement pour compter"""
    return Interface.objects.filter(machine__in=Machine.objects.filter(user__in=all_has_access()).filter(active=True))

def all_active_assigned_interfaces_count():
    """ Version light seulement pour compter"""
    return all_active_interfaces_count().filter(ipv4__isnull=False)

def unassign_ips(user):
    machines = user.user_interfaces()
    for machine in machines:
        unassign_ipv4(machine)
    return

def assign_ips(user):
    """ Assign une ipv4 aux machines d'un user """
    machines = user.user_interfaces()
    for machine in machines:
        if not machine.ipv4:
            interface = assign_ipv4(machine)
            with transaction.atomic(), reversion.create_revision():
                reversion.set_comment("Assignation ipv4")
                interface.save()
    return

def free_ip(type):
    """ Renvoie la liste des ip disponibles """
    if not type.need_infra:
        return IpList.objects.filter(interface__isnull=True).filter(ip_type=type).filter(need_infra=False)
    else:
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
    return render(request, template, c)

@login_required
def new_machine(request, userid):
    try:
        user = User.objects.get(pk=userid)
    except User.DoesNotExist:
        messages.error(request, u"Utilisateur inexistant" )
        return redirect("/machines/")
    if not request.user.has_perms(('cableur',)):
        if user != request.user:
            messages.error(request, "Vous ne pouvez pas ajouter une machine à un autre user que vous sans droit")
            return redirect("/users/profil/" + str(request.user.id))
        if user.user_interfaces().count() >= MAX_INTERFACES:
            messages.error(request, "Vous avez atteint le maximum d'interfaces autorisées que vous pouvez créer vous même (%s) " % MAX_INTERFACES)
            return redirect("/users/profil/" + str(request.user.id))
    machine = NewMachineForm(request.POST or None)
    interface = AddInterfaceForm(request.POST or None, infra=request.user.has_perms(('infra',))) 
    nb_machine = Interface.objects.filter(machine__user=userid).count()
    domain = AliasForm(request.POST or None, infra=request.user.has_perms(('infra',)), name_user=user.surname, nb_machine=nb_machine)
    try:
        if machine.is_valid() and interface.is_valid() and domain.is_valid():
            new_machine = machine.save(commit=False)
            new_machine.user = user
            new_interface = interface.save(commit=False)
            new_domain = domain.save(commit=False)
            if full_domain_validator(request, new_domain):
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
                new_domain.interface_parent = new_interface
                with transaction.atomic(), reversion.create_revision():
                    new_domain.save()
                    reversion.set_user(request.user)
                    reversion.set_comment("Création")
                messages.success(request, "La machine a été crée")
                return redirect("/users/profil/" + str(user.id))
    except TypeError:
        messages.error(request, u"Adresse mac invalide")
    return form({'machineform': machine, 'interfaceform': interface, 'domainform': domain}, 'machines/machine.html', request)

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
    domain_form = AliasForm(request.POST or None, infra=request.user.has_perms(('infra',)), instance=interface.domain)
    try:
        if machine_form.is_valid() and interface_form.is_valid() and domain_form.is_valid():
            new_interface = interface_form.save(commit=False)
            new_machine = machine_form.save(commit=False)
            new_domain = domain_form.save(commit=False)
            if full_domain_validator(request, new_domain):
                with transaction.atomic(), reversion.create_revision():
                    new_machine.save()
                    reversion.set_user(request.user)
                    reversion.set_comment("Champs modifié(s) : %s" % ', '.join(field for field in machine_form.changed_data))
                if free_ip(new_interface.type.ip_type) and not new_interface.ipv4:
                    new_interface = assign_ipv4(new_interface)
                with transaction.atomic(), reversion.create_revision():
                    new_interface.save()
                    reversion.set_user(request.user)
                    reversion.set_comment("Champs modifié(s) : %s" % ', '.join(field for field in interface_form.changed_data))
                with transaction.atomic(), reversion.create_revision():
                    new_domain.save()
                    reversion.set_user(request.user)
                    reversion.set_comment("Champs modifié(s) : %s" % ', '.join(field for field in domain_form.changed_data))
                messages.success(request, "La machine a été modifiée")
                return redirect("/users/profil/" + str(interface.machine.user.id))
    except TypeError:
        messages.error(request, u"Adresse mac invalide")
    return form({'machineform': machine_form, 'interfaceform': interface_form, 'domainform': domain_form}, 'machines/machine.html', request)

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
            return redirect("/users/profil/" + str(machine.user.id))
    if request.method == "POST":
        with transaction.atomic(), reversion.create_revision():
            machine.delete()
            reversion.set_user(request.user)
        messages.success(request, "La machine a été détruite")
        return redirect("/users/profil/" + str(machine.user.id))
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
        if machine.user.user_interfaces().count() >= MAX_INTERFACES:
            messages.error(request, "Vous avez atteint le maximum d'interfaces autorisées que vous pouvez créer vous même (%s) " % MAX_INTERFACES)
            return redirect("/users/profil/" + str(request.user.id))
    interface_form = AddInterfaceForm(request.POST or None, infra=request.user.has_perms(('infra',)))
    domain_form = AliasForm(request.POST or None, infra=request.user.has_perms(('infra',)))
    try:
        if interface_form.is_valid() and domain_form.is_valid():
            new_interface = interface_form.save(commit=False)
            new_interface.machine = machine
            new_domain = domain_form.save(commit=False)
            if full_domain_validator(request, new_domain):
                if free_ip(new_interface.type.ip_type) and not new_interface.ipv4:
                    new_interface = assign_ipv4(new_interface)
                elif not new_interface.ipv4:
                    messages.error(request, u"Il n'y a plus d'ip disponibles")
                with transaction.atomic(), reversion.create_revision():
                    new_interface.save()
                    reversion.set_user(request.user)
                    reversion.set_comment("Création")
                new_domain.interface_parent = new_interface
                with transaction.atomic(), reversion.create_revision():
                    new_domain.save()
                    reversion.set_user(request.user)
                    reversion.set_comment("Création")
                messages.success(request, "L'interface a été ajoutée")
                return redirect("/users/profil/" + str(machine.user.id))
    except TypeError:
        messages.error(request, u"Adresse mac invalide")
    return form({'interfaceform': interface_form, 'domainform': domain_form}, 'machines/machine.html', request)

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
        machine = interface.machine
        with transaction.atomic(), reversion.create_revision():
            interface.delete()
            if not machine.interface_set.all():
               machine.delete()
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
@permission_required('infra')
def add_ns(request):
    ns = NsForm(request.POST or None)
    if ns.is_valid():
        with transaction.atomic(), reversion.create_revision():
            ns.save()
            reversion.set_user(request.user)
            reversion.set_comment("Création")
        messages.success(request, "Cet enregistrement ns a été ajouté")
        return redirect("/machines/index_extension")
    return form({'machineform': ns, 'interfaceform': None}, 'machines/machine.html', request)

@login_required
@permission_required('infra')
def edit_ns(request, nsid):
    try:
        ns_instance = Ns.objects.get(pk=nsid)
    except Ns.DoesNotExist:
        messages.error(request, u"Entrée inexistante" )
        return redirect("/machines/index_extension/")
    ns = NsForm(request.POST or None, instance=ns_instance)
    if ns.is_valid():
        with transaction.atomic(), reversion.create_revision():
            ns.save()
            reversion.set_user(request.user)
            reversion.set_comment("Champs modifié(s) : %s" % ', '.join(field for field in ns.changed_data))
        messages.success(request, "Ns modifié")
        return redirect("/machines/index_extension/")
    return form({'machineform': ns}, 'machines/machine.html', request)

@login_required
@permission_required('infra')
def del_ns(request):
    ns = DelNsForm(request.POST or None)
    if ns.is_valid():
        ns_dels = ns.cleaned_data['ns']
        for ns_del in ns_dels:
            try:
                with transaction.atomic(), reversion.create_revision():
                    ns_del.delete()
                    reversion.set_user(request.user)
                messages.success(request, "Le ns a été supprimée")
            except ProtectedError:
                messages.error(request, "Erreur le Ns suivant %s ne peut être supprimé" % ns_del)
        return redirect("/machines/index_extension")
    return form({'machineform': ns, 'interfaceform': None}, 'machines/machine.html', request)

@login_required
def add_alias(request, interfaceid):
    try:
        interface = Interface.objects.get(pk=interfaceid)
    except Interface.DoesNotExist:
        messages.error(request, u"Interface inexistante" )
        return redirect("/machines")
    if not request.user.has_perms(('cableur',)):
        if interface.machine.user != request.user:
            messages.error(request, "Vous ne pouvez pas ajouter un alias à une machine d'un autre user que vous sans droit")
            return redirect("/users/profil/" + str(request.user.id))
        if Domain.objects.filter(cname__in=Domain.objects.filter(interface_parent__in=interface.machine.user.user_interfaces())).count() >= MAX_ALIAS:
            messages.error(request, "Vous avez atteint le maximum d'alias autorisées que vous pouvez créer vous même (%s) " % MAX_ALIAS)
            return redirect("/users/profil/" + str(request.user.id))
    alias = AliasForm(request.POST or None, infra=request.user.has_perms(('infra',)))
    if alias.is_valid():
        alias = alias.save(commit=False)
        alias.cname = interface.domain
        with transaction.atomic(), reversion.create_revision():
            alias.save()
            reversion.set_user(request.user)
            reversion.set_comment("Création")
        messages.success(request, "Cet alias a été ajouté")
        return redirect("/machines/index_alias/" + str(interfaceid))
    return form({'machineform': alias, 'interfaceform': None}, 'machines/machine.html', request)

@login_required
def edit_alias(request, aliasid):
    try:
        alias_instance = Domain.objects.get(pk=aliasid)
    except Domain.DoesNotExist:
        messages.error(request, u"Entrée inexistante" )
        return redirect("/machines/index_extension/")
    if not request.user.has_perms(('cableur',)) and alias_instance.cname.interface_parent.machine.user != request.user:
        messages.error(request, "Vous ne pouvez pas ajouter un alias à une machine d'un autre user que vous sans droit")
        return redirect("/users/profil/" + str(request.user.id))
    alias = AliasForm(request.POST or None, instance=alias_instance, infra=request.user.has_perms(('infra',)))
    if alias.is_valid():
        with transaction.atomic(), reversion.create_revision():
            alias_instance = alias.save()
            reversion.set_user(request.user)
            reversion.set_comment("Champs modifié(s) : %s" % ', '.join(field for field in alias.changed_data))
        messages.success(request, "Alias modifié")
        return redirect("/machines/index_alias/" + str(alias_instance.cname.interface_parent.id))
    return form({'machineform': alias}, 'machines/machine.html', request)

@login_required
def del_alias(request, interfaceid):
    try:
        interface = Interface.objects.get(pk=interfaceid)
    except Interface.DoesNotExist:
        messages.error(request, u"Interface inexistante" )
        return redirect("/machines")
    if not request.user.has_perms(('cableur',)) and interface.machine.user != request.user:
        messages.error(request, "Vous ne pouvez pas ajouter un alias à une machine d'un autre user que vous sans droit")
        return redirect("/users/profil/" + str(request.user.id))
    alias = DelAliasForm(request.POST or None, interface=interface)
    if alias.is_valid():
        alias_dels = alias.cleaned_data['alias']
        for alias_del in alias_dels:
            try:
                with transaction.atomic(), reversion.create_revision():
                    alias_del.delete()
                    reversion.set_user(request.user)
                messages.success(request, "L'alias %s a été supprimé" % alias_del)
            except ProtectedError:
                messages.error(request, "Erreur l'alias suivant %s ne peut être supprimé" % alias_del)
        return redirect("/machines/index_alias/" + str(interfaceid))
    return form({'machineform': alias, 'interfaceform': None}, 'machines/machine.html', request)

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
def index_alias(request, interfaceid):
    try:
        interface = Interface.objects.get(pk=interfaceid)
    except Interface.DoesNotExist:
        messages.error(request, u"Interface inexistante" )
        return redirect("/machines")
    if not request.user.has_perms(('cableur',)) and interface.machine.user != request.user:
        messages.error(request, "Vous ne pouvez pas éditer une machine d'un autre user que vous sans droit")
        return redirect("/users/profil/" + str(request.user.id))
    alias_list = Domain.objects.filter(cname=Domain.objects.filter(interface_parent=interface)).order_by('name')
    return render(request, 'machines/index_alias.html', {'alias_list':alias_list, 'interface_id': interfaceid})

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
    elif object == 'alias':
        try:
             object_instance = Domain.objects.get(pk=id)
        except Domain.DoesNotExist:
             messages.error(request, "Alias inexistant")
             return redirect("/machines/")
        if not request.user.has_perms(('cableur',)) and object_instance.cname.interface_parent.machine.user != request.user:
             messages.error(request, "Vous ne pouvez pas afficher l'historique d'un alias d'un autre user que vous sans droit cableur")
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
    elif object == 'ns' and request.user.has_perms(('cableur',)):
        try:
             object_instance = Ns.objects.get(pk=id)
        except Ns.DoesNotExist:
             messages.error(request, "Ns inexistant")
             return redirect("/machines/")
    else:
        messages.error(request, "Objet  inconnu")
        return redirect("/machines/")
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


""" Framework Rest """

class JSONResponse(HttpResponse):
    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)

@csrf_exempt
@login_required
@permission_required('serveur')
def mac_ip_list(request):
    interfaces = all_active_assigned_interfaces()
    seria = InterfaceSerializer(interfaces, many=True)
    return seria.data

@csrf_exempt
@login_required
@permission_required('serveur')
def alias(request):
    alias = Domain.objects.filter(interface_parent=None).filter(cname=Domain.objects.filter(interface_parent__in=Interface.objects.exclude(ipv4=None))).select_related('extension')
    seria = DomainSerializer(alias, many=True)
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
def mx(request):
    mx = Mx.objects.all()
    seria = MxSerializer(mx, many=True)
    return JSONResponse(seria.data)

@csrf_exempt
@login_required
@permission_required('serveur')
def ns(request):
    ns = Ns.objects.exclude(ns__in=Domain.objects.filter(interface_parent__in=Interface.objects.filter(ipv4=None)))
    seria = NsSerializer(ns, many=True)
    return JSONResponse(seria.data)

@csrf_exempt
@login_required
@permission_required('serveur')
def zones(request):
    zones = Extension.objects.all()
    seria = ExtensionSerializer(zones, many=True)
    return JSONResponse(seria.data)

@csrf_exempt
@login_required
@permission_required('serveur')
def mac_ip(request):
    seria = mac_ip_list(request)
    return JSONResponse(seria)

@csrf_exempt
@login_required
@permission_required('serveur')
def mac_ip_dns(request):
    seria = mac_ip_list(request)
    return JSONResponse(seria)

@csrf_exempt
def login_user(request):
    user = authenticate(username=request.POST['username'], password=request.POST['password'])
    login(request, user)
    return HttpResponse("Logged In")
