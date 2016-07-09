from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.db import IntegrityError

from topologie.models import Switch, Port
from topologie.forms import EditPortForm, EditSwitchForm, AddPortForm
from users.views import form

@login_required
def index(request):
    is_infra = request.user.has_perms(('infra',))
    switch_list = Switch.objects.order_by('building', 'number')
    return render(request, 'topologie/index.html', {'switch_list': switch_list, 'is_infra':is_infra})

@login_required
def index_port(request, switch_id):
    is_infra = request.user.has_perms(('infra',))
    try:
        switch = Switch.objects.get(pk=switch_id)
    except Switch.DoesNotExist:
        messages.error(request, u"Switch inexistant")
        return redirect("/topologie/")
    port_list = Port.objects.filter(switch = switch).order_by('port')
    return render(request, 'topologie/index_p.html', {'port_list':port_list, 'id_switch':switch_id, 'nom_switch':switch, 'is_infra':is_infra})

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
            port.save()
            messages.success(request, "Port ajouté")
        except IntegrityError:
            messages.error(request,"Ce port existe déjà" )
        return redirect("/topologie/switch/" + switch_id)
    return form({'topoform':port}, 'topologie/port.html', request)

@login_required
@permission_required('infra')
def edit_port(request, port_id):
    try:
        port = Port.objects.get(pk=port_id)
    except Port.DoesNotExist:
        messages.error(request, u"Port inexistant")
        return redirect("/topologie/")
    port = EditPortForm(request.POST or None, instance=port)
    if port.is_valid():
        port.save()
        messages.success(request, "Le port a bien été modifié")
        return redirect("/topologie/")
    return form({'topoform':port}, 'topologie/port.html', request)

@login_required
@permission_required('infra')
def new_switch(request):
    switch = EditSwitchForm(request.POST or None)
    if switch.is_valid():
        switch.save()
        messages.success(request, "Le switch a été créé")
        return redirect("/topologie/")
    return form({'topoform':switch}, 'topologie/port.html', request)

@login_required
@permission_required('infra')
def edit_switch(request, switch_id):
    try:
        switch = Switch.objects.get(pk=switch_id)
    except Switch.DoesNotExist:
        messages.error(request, u"Switch inexistant")
        return redirect("/topologie/")
    switch = EditSwitchForm(request.POST or None, instance=switch)
    if switch.is_valid():
        switch.save()
        messages.success(request, "Le switch a bien été modifié")
        return redirect("/topologie/")
    return form({'topoform':switch}, 'topologie/port.html', request)
