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

from .models import Port, Switch, Room
from django.forms import ModelForm, Form

class PortForm(ModelForm):
    class Meta:
        model = Port
        fields = '__all__'

class EditPortForm(ModelForm):
    class Meta(PortForm.Meta):
        fields = ['room', 'related', 'radius', 'details']

#    def __init__(self, *args, **kwargs):
#        super(EditPortForm, self).__init__(*args, **kwargs)
#        self.fields['related'].queryset = Port.objects.all().order_by('switch', 'port')

class AddPortForm(ModelForm):
    class Meta(PortForm.Meta):
        fields = ['port', 'room', 'machine_interface', 'related', 'radius', 'details']

class EditSwitchForm(ModelForm):
    class Meta:
        model = Switch
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(EditSwitchForm, self).__init__(*args, **kwargs)
        self.fields['location'].label = 'Localisation'
        self.fields['number'].label = 'Nombre de ports'

class NewSwitchForm(ModelForm):
    class Meta(EditSwitchForm.Meta):
        fields = ['location', 'number', 'details']

class EditRoomForm(ModelForm):
    class Meta:
        model = Room
        fields = '__all__'
