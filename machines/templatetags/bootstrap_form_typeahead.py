# -*- mode: python; coding: utf-8 -*-
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

        choices
            A string representing the choices in JS. The choices must be an
            array of objects. Each of those objects must at least have the
            fields 'key' (value to send) and 'value' (value to display).
            Other fields can be added as desired.
            If not specified, the key is the id of the object and the value
            is its string representation as in a normal bootstrap form.
            Example :
            choices='[{key:0,value:"choice0",extrafield:"data0"}, {...},...];'

        match_func
            A string representing a valid JS function used in the dataset to
            overload the matching engine. This function is used the source of
            the dataset. This function receives 2 parameters, the query and
            the synchronize function as specified in typeahead.js documentation.
            If needed, the local variables 'choices' and 'engine' contains
            respectively the array of possible values and the engine to match
            queries with possible values.
            If not specified, the function used display up to the 10 first
            elements if the query is empty and else the matching results.
            Example :
            match_func='function(q, sync) { engine.search(q, sync); }'

        See boostrap_form_ for other arguments

    **Usage**::

        {% bootstrap_form_typeahead form ['field1[,field2[,...]]] %}

    **Example**:

        {% bootstrap_form_typeahead form 'ipv4' choices='[...]' %}
    """


    t_fields = typeahead_fields.split(',')
    exclude = kwargs.get('exclude', None)
    exclude = exclude.split(',') if exclude else []
    t_choices = kwargs.get('choices', {})
    t_match_func = kwargs.get('match_func', {})
    hidden = [h.name for h in django_form.hidden_fields()]

    form = ''
    for f_name, f_value in django_form.fields.items() :
        if not f_name in exclude :
            if f_name in t_fields and not f_name in hidden :
                    f_bound = f_value.get_bound_field( django_form, f_name )
                    f_value.widget = TextInput(
                        attrs={
                            'name': 'typeahead_'+f_name,
                            'placeholder': f_value.empty_label
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
                        typeahead_js(
                            f_name,
                            f_value,
                            t_choices,
                            t_match_func
                        )
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

def typeahead_js( f_name, f_value, t_choices, t_match_func ) :

    choices = mark_safe(t_choices[f_name]) if f_name in t_choices.keys()      \
         else default_choices( f_value )

    match_func = mark_safe(t_match_func[f_name])                              \
              if f_name in t_match_func.keys()                                \
            else default_match_func( f_name )

    js_content =                                                              \
        'var choices_'+f_name+' = ' + choices + ';\n'                       + \
        'var setup_'+f_name+' = function() {\n'                             + \
            'var engine_'+f_name+' = ' + default_engine() + ';\n'           + \
            '$("#'+input_id(f_name) + '").typeahead("destroy");\n'          + \
            '$("#'+input_id(f_name) + '").typeahead(\n'                     + \
                default_datasets( f_name, match_func ) + '\n'               + \
            ');\n'                                                          + \
            reset_input( f_name, f_value ) + '\n'                           + \
        '};\n'                                                              + \
        '$("#'+input_id(f_name) + '").bind(\n'                              + \
            '"typeahead:select", '                                          + \
            typeahead_updater( f_name ) + '\n'                              + \
        ').bind(\n'                                                         + \
            '"typeahead:change", '                                          + \
            typeahead_change( f_name ) + '\n'                               + \
        ');\n'
    js_content += '$("#'+input_id(f_name)+'").ready( setup_'+f_name+' );\n'

    return render_tag( 'script', content=mark_safe( js_content ) )

def reset_input( f_name, f_value ) :
    return '$("#'+input_id(f_name)+'").typeahead("val","");\n'                \
        '$("#'+hidden_id(f_name)+'").val("");'

def default_choices( f_value ) :
    return '[' +                                                              \
        ', '.join([                                                           \
            '{key: ' + (str(choice[0]) if choice[0] != '' else '""') +        \
            ', value: "' + str(choice[1]) + '"}'                              \
            for choice in f_value.choices                                     \
            ]) +                                                              \
        ']'

def default_engine ( f_name ) :
    return 'new Bloodhound({ '                                                \
            'datumTokenizer: Bloodhound.tokenizers.obj.whitespace("value"), ' \
            'queryTokenizer: Bloodhound.tokenizers.whitespace, '              \
            'local: choices_'+f_name+', '                                     \
            'identify: function(obj) { return obj.key; } '                    \
        '})'

def default_datasets( f_name, match_func ) :
    return '{ '                                                               \
            'hint: true, '                                                    \
            'highlight: true, '                                               \
            'minLength: 0 '                                                   \
        '}, '                                                                 \
        '{ '                                                                  \
            'display: "value", '                                              \
            'name: "'+f_name+'", '                                            \
            'source: '+match_func +                                           \
        '}'

def default_match_func ( f_name ) :
    return 'function(q, sync) {'                                              \
        'if (q === "") {'                                                     \
            'var nb = 10;'                                                    \
            'var first = [] ;'                                                \
            'for ( var i=0 ; i<nb && i<choices_'+f_name+'.length; i++ ) {'    \
                'first.push(choices_'+f_name+'[i].key);'                      \
            '}'                                                               \
            'sync(engine_'+f_name+'.get(first));'                             \
        '} else {'                                                            \
            'engine_'+f_name+'.search(q, sync);'                              \
        '}'                                                                   \
    '}'

def typeahead_updater( f_name ):
    return 'function(evt, item) { '                                           \
        '$("#'+hidden_id(f_name)+'").val( item.key ); '                       \
        '$("#'+hidden_id(f_name)+'").change();'                               \
        'return item; '                                                       \
    '}'

def typeahead_change( f_name ):
    return 'function(evt) { '                                                 \
        'if ($("#'+input_id(f_name)+'").typeahead("val") === "") {'           \
            '$("#'+hidden_id(f_name)+'").val(""); '                           \
            '$("#'+hidden_id(f_name)+'").change();'                           \
        '}'                                                                   \
    '}'
