from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import IntegrityError

from topologie.models import Switch, Port
from topologie.forms import EditPortForm, EditSwitchForm, AddPortForm
from users.views import form


def index(request):
    switch_list = Switch.objects.order_by('building', 'number')
    return render(request, 'topologie/index.html', {'switch_list': switch_list})

def index_port(request, switch_id):
    try:
        switch = Switch.objects.get(pk=switch_id)
    except Switch.DoesNotExist:
        messages.error(request, u"Switch inexistant")
        return redirect("/topologie/")
    port_list = Port.objects.filter(switch = switch).order_by('port')
    return render(request, 'topologie/index_p.html', {'port_list':port_list, 'id_switch':switch_id, 'nom_switch':switch})

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
            pass
        return redirect("/topologie/switch/" + switch_id)
    return form({'topoform':port}, 'topologie/port.html', request)

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
       
def new_switch(request):
    switch = EditSwitchForm(request.POST or None)
    if switch.is_valid():
        switch.save()
        messages.success(request, "Le switch a été créé")
        return redirect("/topologie/")
    return form({'topoform':switch}, 'topologie/port.html', request)

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
