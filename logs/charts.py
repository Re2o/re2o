from jchart import Chart
from jchart.config import Axes

from users.models import User, Adherent
from re2o.utils import all_adherent

from datetime import timedelta
from django.utils import timezone
from django.db.models import Count

class ActiveUserChart(Chart):
    """Create the hart of all active users for the 3 last months"""
    chart_type = 'line'
    scales = {'xAxes': [Axes(type='time', position='bottom')]}


    def get_datasets(self, **kwargs):
        data=[]
        for i in range(100):
            d = timedelta(days=i)
            date = timezone.now()-d
            data.append({'x':date,'y':all_adherent(search_time=date).count()})

        return [{
            'type': 'line',
            'label': "Nombre d'utilisateur actifs",
            'data': data
        }]

class MachinePerUserChart(Chart):
    """Create the chart displaying the number of machines per users
    for the 20 firsts users"""

    qs = User.objects.annotate(num=Count('machine')).order_by('-num')[:20]

    chart_type = 'bar'
    scales = {'xAxes': [Axes(type='category', position='bottom',)]}

    def get_labels(self, **kwargs):
        qs = User.objects.annotate(num=Count('machine')).order_by('-num')[:20]
        return [u.name for u in qs]

    def get_datasets(self, **kwargs):
        qs = User.objects.annotate(num=Count('machine')).order_by('-num')[:20]
        data=[u.num for u in qs]

        return [{
            'label': "Nombre de machines par utilisateurs",
            'data': data
        }]
