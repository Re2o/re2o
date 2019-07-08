from django.shortcuts import render

from .models import(
    Ticket
)

def new_ticket(request,user):
    """ Vue de création d'un ticket """
    ticket = NewTicketForm(request.POST or None, user=request.user)
    if ticket.is_valid():
        new_ticket_obj = machine.save(commit=False)
        nex_ticket_obj.user = user
        new_machine_obj.save()

    return form(
        {
            'ticketform':ticket,
        },
        'ticket/ticket.html',
        request
    )

def aff_ticket(request,ticketid):
    """Vue d'affichage d'un ticket"""
    ticket = Ticket.objects.filter(id=ticketid).get()
    return render(request,'tickets/aff_ticket.html',{'ticket':ticket})
    
def aff_tickets(request):
    """ Vue d'affichage de tout les tickets """
    tickets = Ticket.objects.all()
    return render(request,'tickets/aff_tickets.html',
                    {'tickets_list':tickets})
