# App de gestion des statistiques pour re2o
# Gabriel Détraz
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

from reversion.models import Revision
from reversion.models import Version

from re2o.settings import PAGINATION_NUMBER, PAGINATION_LARGE_NUMBER

@login_required
@permission_required('cableur')
def index(request):
    revisions = Revision.objects.all().order_by('date_created').reverse()
    paginator = Paginator(revisions, PAGINATION_NUMBER)
    page = request.GET.get('page')
    try:
        revisions = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        revisions = paginator.page(1)
    except EmptyPage:
     # If page is out of range (e.g. 9999), deliver last page of results.
        revisions = paginator.page(paginator.num_pages)
    return render(request, 'logs/index.html', {'revisions_list': revisions})

