from django.forms.widgets import Input
from django.forms.utils import flatatt
from django.utils.safestring import mark_safe
from django.template import Context, Template
from django.template.loader import get_template

class DateTimePicker(Input):
    def render(self, name, value, attrs=None):
        super().render(name, value, attrs)
        flat_attrs = flatatt(attrs)
        html = '''{% load static %}<script src="{% static 'js/jquery-2.2.4.min.js' %}"></script><script src="{% static 'js/jquery-ui-1.12.1/jquery-ui.min.js' %}"></script><script src="{% static 'js/jquery-ui-timepicker-addon.js' %}"></script><link href="{% static 'js/jquery-ui-1.12.1/jquery-ui.min.css' %}" rel="stylesheet"/><link href="{% static 'css/jquery-ui-timepicker-addon.css' %}" rel="stylesheet"/>'''
        html += '''<input %(attrs)s name="datetimepicker" type="text" class="form-control" id="datetimepicker"/>
        <script>
            $(document).ready(function(){
                $("#%(id)s").datetimepicker({
                    dateFormat:'yy-mm-dd',
                    timeFormat: 'HH:mm:ss',
                    })
                });
        </script>'''%{'attrs':flat_attrs, 'id':attrs['id']}
        template = Template(html)
        context = Context({})
        return template.render(context)
