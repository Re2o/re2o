from django.contrib import messages
from django.shortcuts import render, redirect
from django.urls import reverse
from django.forms import modelformset_factory
from re2o.views import form

from .models import(
    Ticket
)

from .forms import (
    NewTicketForm
)

def new_ticket(request):
    """ Vue de création d'un ticket """
    ticketform = NewTicketForm(request.POST or None)#, user=request.user)

    if request.method == 'POST':
        ticketform = NewTicketForm(request.POST)

        if ticketform.is_valid():
            ticket = ticketform.save(commit=False)
            ticket.user = request.user
            ticket.save()
            messages.success(request,'Votre ticket à été ouvert. Nous vous répondront le plus rapidement possible.')
            return redirect(reverse('users:profil',kwargs={'userid':str(request.user.id)}))
        else:
            messages.error(request, 'Formulaire invalide')
    else:
        ticketform = NewTicketForm
    return form({'ticketform':ticketform,},'tickets/form_ticket.html',request)

def aff_ticket(request,ticketid):
    """Vue d'affichage d'un ticket"""
    ticket = Ticket.objects.filter(id=ticketid).get()
    return render(request,'tickets/aff_ticket.html',{'ticket':ticket})
    
def aff_tickets(request):
    """ Vue d'affichage de tout les tickets """
    tickets = Ticket.objects.all().order_by('date')
    return render(request,'tickets/index.html',
                    {'tickets_list':tickets})
