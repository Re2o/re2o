from django.contrib import messages
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.urls import reverse
from django.forms import modelformset_factory
from re2o.views import form

from .models import(
    Ticket,
    Preferences,
)

from .forms import (
    NewTicketForm,
    EditPreferencesForm,
)


def new_ticket(request):
    """ Vue de création d'un ticket """
    ticketform = NewTicketForm(request.POST or None)

    if request.method == 'POST':
        ticketform = NewTicketForm(request.POST)

        if ticketform.is_valid():
            email = ticketform.cleaned_data.get('email')
            ticket = ticketform.save(commit=False)
            #raise ValueError("email: {} type: {}".format(email,type(email))) 
            if request.user.is_authenticated:
                ticket.user = request.user
                ticket.save()
                messages.success(request,'Votre ticket à été ouvert. Nous vous répondront le plus rapidement possible.')
                return redirect(reverse('users:profil',kwargs={'userid':str(request.user.id)}))
            if not request.user.is_authenticated and email != "":
                ticket.save()
                messages.success(request,'Votre ticket à été ouvert. Nous vous répondront le plus rapidement possible.')
                return redirect(reverse('index'))
            else:    
                messages.error(request,"Vous n'êtes pas authentifié, veuillez vous authentifier ou fournir une adresse mail pour que nous puissions vous recontacter")
                return form({'ticketform':ticketform,},'tickets/form_ticket.html',request)
            
    else:
        ticketform = NewTicketForm
    return form({'ticketform':ticketform,},'tickets/form_ticket.html',request)

def aff_ticket(request,ticketid):
    """Vue d'affichage d'un ticket"""
    ticket = Ticket.objects.filter(id=ticketid).get()
    return render(request,'tickets/aff_ticket.html',{'ticket':ticket})
    
def aff_tickets(request):
    """ Vue d'affichage de tout les tickets """
    tickets = Ticket.objects.all().order_by('-date')
    return render(request,'tickets/index.html',
                    {'tickets_list':tickets})

def edit_preferences(request):
    """ Vue d'édition des préférences des tickets """

    preferences_instance, created = Preferences.objects.get_or_create(id=1)
    preferencesform = EditPreferencesForm(
        request.POST or None,
        instance = preferences_instance,)
    
    if preferencesform.is_valid():
        if preferencesform.changed_data:
            preferencesform.save()
            messages.success(request,'Préférences des Tickets mises à jour')
            return redirect(reverse('preferences:display-options',))
        else:
            messages.error(request,'Formulaire Invalide')
            return form({'preferencesform':preferencesform,},'tickets/form_preferences.html',request)
    return form({'preferencesform':preferencesform,},'tickets/form_preferences.html',request)
    
# views cannoniques des apps optionnels    
def profil(request,user):
    """ Vue cannonique d'affichage des tickets dans l'accordeon du profil"""
    tickets = Ticket.objects.filter(user=user).all().order_by('-date')
    context = {'tickets_list':tickets}
    return render_to_string('tickets/profil.html', context=context, request=request, using=None)

def preferences(request):
    """ Vue cannonique d'affichage des tickets dans l'affichage du profil"""
    preferences = Preferences.objects.first()
    context = {'preferences':preferences}
    return render_to_string('tickets/preferences.html', context=context, request=request, using=None)
