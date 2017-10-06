# Re2o est un logiciel d'administration développé initiallement au rezometz. Il
# se veut agnostique au réseau considéré, de manière à être installable en
# quelques clics.
# 
# Copyright © 2017  Maël Kervella
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

from django import template
from django.utils.safestring import mark_safe
from django.forms import TextInput
from bootstrap3.templatetags.bootstrap3 import bootstrap_form
from bootstrap3.utils import render_tag
from bootstrap3.forms import render_field

register = template.Library()

@register.simple_tag
def bootstrap_form_typeahead(django_form, typeahead_fields, *args, **kwargs):
    """
    Render a form where some specific fields are rendered using Typeahead.
    Using Typeahead really improves the performance, the speed and UX when
    dealing with very large datasets (select with 50k+ elts for instance).
    For convenience, it accepts the same parameters as a standard bootstrap
    can accept.

    **Tag name**::

        bootstrap_form_typeahead

    **Parameters**:
        
        form
            The form that is to be rendered

        typeahead_fields
            A list of field names (comma separated) that should be rendered
            with typeahead instead of the default bootstrap renderer.

        See boostrap_form_ for other arguments

    **Usage**::

        {% bootstrap_form_typeahead form ['field1[,field2[,...]]] %}

    **Example**:
        
        {% bootstrap_form_typeahead form 'ipv4' %}
    """

    t_fields = typeahead_fields.split(',')
    exclude = kwargs.get('exclude', None)
    exclude = exclude.split(',') if exclude else []
    hidden = [h.name for h in django_form.hidden_fields()]
    
    form = ''
    for f_name, f_value in django_form.fields.items() :
        if not f_name in exclude :
            if f_name in t_fields and not f_name in hidden :
                    f_bound = f_value.get_bound_field( django_form, f_name )
                    f_value.widget = TextInput(
                        attrs={
                            'name': 'typeahead_'+f_name,
                        }
                    )
                    form += render_field(
                        f_value.get_bound_field( django_form, f_name ),
                        *args,
                        **kwargs
                    )
                    form += render_tag(
                        'div',
                        attrs = {'class': 'form-group'},
                        content = hidden_tag( f_bound, f_name ) +
                        typeahead_full_script( f_name, f_value )
                    )
            else:
                form += render_field(
                    f_value.get_bound_field(django_form, f_name),
                    *args,
                    **kwargs
                )


    return mark_safe( form )

def input_id( f_name ) :
    return 'id_'+f_name

def hidden_id( f_name ):
    return 'typeahead_hidden_'+f_name

def hidden_tag( f_bound, f_name ):
    return render_tag(
        'input',
        attrs={
            'id': hidden_id(f_name),
            'name': f_name,
            'type': 'hidden',
            'value': f_bound.value()
        }
    )

def typeahead_full_script( f_name, f_value ) :
    js_content =                                                              \
        '$("#'+input_id(f_name)+'").ready( function() {\n'                  + \
            reset_input( f_name, f_value ) + '\n'                           + \
            typeahead_choices( f_value ) + '\n'                             + \
            typeahead_engine () + '\n'                                      + \
            '$("#'+input_id(f_name) + '").typeahead(\n'                     + \
                typeahead_datasets( f_name )                                + \
            ').bind(\n'                                                     + \
                '"typeahead:select", '                                      + \
                typeahead_updater( f_name ) + '\n'                          + \
            ')\n'                                                           + \
        '});\n'

    return render_tag( 'script', content=mark_safe( js_content ) )

def reset_input( f_name, f_value ) :
    return '$("#'+input_id(f_name)+'").val("'+f_value.empty_label+'");'

def typeahead_choices( f_value ) :
    return 'var choices = [' +                                                \
        ', '.join([                                                           \
            '{key: ' + (str(choice[0]) if choice[0] != '' else '""') +        \
            ', value: "' + str(choice[1]) + '"}'                              \
            for choice in f_value.choices                                     \
            ]) +                                                              \
        '];'

def typeahead_engine () :
    return 'var engine = new Bloodhound({ '                                   \
            'datumTokenizer: Bloodhound.tokenizers.obj.whitespace("value"), ' \
            'queryTokenizer: Bloodhound.tokenizers.whitespace, '              \
            'local: choices, '                                                \
            'identify: function(obj) { return obj.value; } '                  \
        '});'

def typeahead_datasets( f_name ) :
    return '{ '                                                               \
            'hint: true, '                                                    \
            'highlight: true, '                                               \
            'minLength: 0 '                                                   \
        '}, '                                                                 \
        '{ '                                                                  \
            'templates: { '                                                   \
                'suggestion: Handlebars.compile("<div>{{value}}</div>") '     \
            '}, '                                                             \
            'display: "value", '                                              \
            'name: "'+f_name+'", '                                            \
            'source: function(q, sync) {'                                     \
                'if (q === "") {'                                             \
                    'var nb = 10;'                                            \
                    'var first = [] ;'                                        \
                    'for ( var i = 0 ; i < nb ; i++ ) {'                      \
                        'first.push(choices[i].value);'                       \
                    '}'                                                       \
                    'sync(engine.get(first));'                                \
                '} else {'                                                    \
                    'engine.search(q, sync)'                                  \
                '}'                                                           \
            '}'                                                               \
        '}'

def typeahead_updater( f_name ):
    return 'function(evt, item) { '                                           \
        '$("#'+hidden_id(f_name)+'").val( item.key ); '                       \
        'return item; '                                                       \
        '}'

