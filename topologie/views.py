from django.shortcuts import render, redirect
from django.contrib import messages


from topologie.models import Switch, Port
from topologie.forms import EditPortForm
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
    return render(request, 'topologie/index_p.html', {'port_list':port_list})

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
        return redirect("/topologie")
    return form({'topoform':port}, 'topologie/port.html', request)
        
