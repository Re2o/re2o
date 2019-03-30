from django.core.management.base import BaseCommand

from re2o.utils import all_adherent

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.dates import (YEARLY, DateFormatter,rrulewrapper, RRuleLocator, drange)
from dateutil.rrule import MONTHLY

from datetime import datetime
from datetime import timedelta
import pytz


class Command(BaseCommand):
    help="Génère le graphe des adhérents entre la date de départ et de fin passées en argument au format 'JJ/MM/AAAA' "

    def add_arguments(self, parser):
        parser.add_argument('date_start', type=str, help='Start date DD/MM/YYYY')
        parser.add_argument('date_stop', type=str, help='Stop date DD/MM/YYYY')

    def handle(self, *args, **kwargs):
        try: 
            date_start=datetime.strptime(kwargs['date_start'],'%d/%m/%Y')
            date_stop=datetime.strptime(kwargs['date_stop'],'%d/%m/%Y')
        except ValueError:
            raise ValueError("The dates you entered do not follow the 'DD/MM/YYYY' format")
        
        date_start = pytz.utc.localize(date_start)
        date_stop = pytz.utc.localize(date_stop)
        delta = timedelta(days=10)
        dates = [date_start]
        count = [all_adherent(date_start).count()]
        
        while dates[-1]+delta < date_stop:
            dates.append(dates[-1]+delta)
            count.append(all_adherent(dates[-1]).count())

        rule = rrulewrapper(MONTHLY, interval=5)
        loc = RRuleLocator(rule)
        formatter = DateFormatter('%d/%m/%y')

        fig, ax = plt.subplots()
        plt.plot_date(dates, count,'.')
        ax.xaxis.set_major_locator(loc)
        ax.xaxis.set_major_formatter(formatter)
        plt.xticks(rotation=45,size=10)
        
        plt.savefig('graph_adhesion.png')
