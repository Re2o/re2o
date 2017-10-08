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

        bft_param
            A dict of parameters for the bootstrap_form_typeahead tag. The
            possible parameters are the following.

            choices
                A dict of strings representing the choices in JS. The keys of
                the dict are the names of the concerned fields. The choices
                must be an array of objects. Each of those objects must at
                least have the fields 'key' (value to send) and 'value' (value
                to display). Other fields can be added as desired.
                For a more complex structure you should also consider
                reimplementing the engine and the match_func.
                If not specified, the key is the id of the object and the value
                is its string representation as in a normal bootstrap form.
                Example :
                'choices' : {
                 'field_A':'[{key:0,value:"choice0",extra:"data0"},{...},...]',
                 'field_B':...,
                 ...
                 }

            engine
                A dict of strings representating the engine used for matching
                queries and possible values with typeahead. The keys of the
                dict are the names of the concerned fields. The string is valid
                JS code.
                If not specified, BloodHound with relevant basic properties is
                used.
                Example :
                'engine' : {'field_A': 'new Bloodhound()', 'field_B': ..., ...}

            match_func
                A dict of strings representing a valid JS function used in the
                dataset to overload the matching engine. The keys of the dict
                are the names of the concerned fields. This function is used
                the source of the dataset. This function receives 2 parameters,
                the query and the synchronize function as specified in
                typeahead.js documentation. If needed, the local variables
                'choices_<fieldname>' and 'engine_<fieldname>' contains
                respectively the array of all possible values and the engine
                to match queries with possible values.
                If not specified, the function used display up to the 10 first
                elements if the query is empty and else the matching results.
                Example :
                'match_func' : {
                 'field_A': 'function(q, sync) { engine.search(q, sync); }',
                 'field_B': ...,
                 ...
                }

            update_on
                A dict of list of ids that the values depends on. The engine
                and the typeahead properties are recalculated and reapplied.
                Example :
                'addition' : {
                 'field_A' : [ 'id0', 'id1', ... ] ,
                 'field_B' : ... ,
                 ...
                }

        See boostrap_form_ for other arguments

    **Usage**::

        {% bootstrap_form_typeahead
            form
            [ '<field1>[,<field2>[,...]]' ]
            [ {
                [ 'choices': {
                    [  '<field1>': '<choices1>'
                    [, '<field2>': '<choices2>'
                    [, ... ] ] ]
                } ]
                [, 'engine': {
                    [  '<field1>': '<engine1>'
                    [, '<field2>': '<engine2>'
                    [, ... ] ] ]
                } ]
                [, 'match_func': {
                    [  '<field1>': '<match_func1>'
                    [, '<field2>': '<match_func2>'
                    [, ... ] ] ]
                } ]
                [, 'update_on': {
                    [  '<field1>': '<update_on1>'
                    [, '<field2>': '<update_on2>'
                    [, ... ] ] ]
                } ]
            } ]
            [ <standard boostrap_form parameters> ]
        %}

    **Example**:

        {% bootstrap_form_typeahead form 'ipv4' choices='[...]' %}
    """

    t_fields = typeahead_fields.split(',')
    params = kwargs.get('bft_param', {})
    exclude = params.get('exclude', None)
    exclude = exclude.split(',') if exclude else []
    t_choices = params.get('choices', {})
    t_engine = params.get('engine', {})
    t_match_func = params.get('match_func', {})
    t_update_on = params.get('update_on', {})
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
                        content = hidden_tag( f_bound, f_name ) +
                        typeahead_js(
                            f_name,
                            f_value,
                            f_bound,
                            t_choices,
                            t_engine,
                            t_match_func,
                            t_update_on
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
    """ The id of the HTML input element """
    return 'id_'+f_name

def hidden_id( f_name ):
    """ The id of the HTML hidden input element """
    return 'typeahead_hidden_'+f_name

def hidden_tag( f_bound, f_name ):
    """ The HTML hidden input element """
    return render_tag(
        'input',
        attrs={
            'id': hidden_id(f_name),
            'name': f_name,
            'type': 'hidden',
            'value': f_bound.value() or ""
        }
    )

def typeahead_js( f_name, f_value, f_bound,
        t_choices, t_engine, t_match_func, t_update_on ) :
    """ The whole script to use """

    choices = mark_safe( t_choices[f_name] ) if f_name in t_choices.keys()    \
        else default_choices( f_value )

    engine = mark_safe( t_engine[f_name] ) if f_name in t_engine.keys()       \
        else default_engine ( f_name )

    match_func = mark_safe(t_match_func[f_name])                              \
        if f_name in t_match_func.keys() else default_match_func( f_name )

    update_on = t_update_on[f_name] if f_name in t_update_on.keys() else []

    js_content = (
        'var choices_{f_name} = {choices};'
        'var engine_{f_name};'
        'var setup_{f_name} = function() {{'
            'engine_{f_name} = {engine};'
            '$( "#{input_id}" ).typeahead( "destroy" );'
            '$( "#{input_id}" ).typeahead( {datasets} );'
        '}};'
        '$( "#{input_id}" ).bind( "typeahead:select", {updater} );'
        '$( "#{input_id}" ).bind( "typeahead:change", {change} );'
        '{updates}'
        '$( "#{input_id}" ).ready( function() {{'
            'setup_{f_name}();'
            '{init_input}'
        '}} );'
        ).format(
                f_name = f_name,
                choices = choices,
                engine = engine,
                input_id = input_id( f_name ),
                datasets = default_datasets( f_name, match_func ),
                updater = typeahead_updater( f_name ),
                change = typeahead_change( f_name ),
                updates = ''.join( [ (
                    '$( "#{u_id}" ).change( function() {{'
                        'setup_{f_name}();'
                        '{reset_input}'
                    '}} );'
                    ).format(
                        u_id = u_id,
                        reset_input = reset_input( f_name ),
                        f_name = f_name
                    ) for u_id in update_on ]
                ),
                init_input = init_input( f_name, f_bound ),
        )

    return render_tag( 'script', content=mark_safe( js_content ) )

def init_input( f_name, f_bound ) :
    """ The JS script to init the fields values """
    init_key = f_bound.value() or '""'
    return (
        '$( "#{input_id}" ).typeahead("val", {init_val});'
        '$( "#{hidden_id}" ).val( {init_key} );'
        ).format(
                input_id = input_id( f_name ),
                init_val = '""' if init_key == '""' else
                    'engine_{f_name}.get( {init_key} )[0].value'.format(
                        f_name = f_name,
                        init_key = init_key
                    ),
                init_key = init_key,
                hidden_id = hidden_id( f_name )
        )

def reset_input( f_name ) :
    """ The JS script to reset the fields values """
    return (
        '$( "#{input_id}" ).typeahead("val", "");'
        '$( "#{hidden_id}" ).val( "" );'
        ).format(
                input_id = input_id( f_name ),
                hidden_id = hidden_id( f_name )
        )

def default_choices( f_value ) :
    """ The JS script creating the variable choices_<fieldname> """
    return '[ {objects} ]'.format(
            objects = ', '.join(
                [ '{{ key: {k}, value: "{k}" }}'.format(
                    k = choice[0] if choice[0] != '' else '""',
                    v = choice[1]
                ) for choice in f_value.choices ]
            )
        )

def default_engine ( f_name ) :
    """ The JS script creating the variable engine_<field_name> """
    return (
        'new Bloodhound({{'
            'datumTokenizer: Bloodhound.tokenizers.obj.whitespace("value"),'
            'queryTokenizer: Bloodhound.tokenizers.whitespace,'
            'local: choices_{f_name},'
            'identify: function(obj) {{ return obj.key; }}'
        '}})'
        ).format(
                f_name = f_name
        )

def default_datasets( f_name, match_func ) :
    """ The JS script creating the datasets to use with typeahead """
    return (
        '{{'
            'hint: true,'
            'highlight: true,'
            'minLength: 0'
        '}},'
        '{{'
            'display: "value",'
            'name: "{f_name}",'
            'source: {match_func}'
        '}}'
        ).format(
                f_name = f_name,
                match_func = match_func
        )

def default_match_func ( f_name ) :
    """ The JS script creating the matching function to use with typeahed """
    return (
        'function ( q, sync ) {{'
            'if ( q === "" ) {{'
                'var first = choices_{f_name}.slice( 0, 5 ).map('
                    'function ( obj ) {{ return obj.key; }}'
                ');'
                'sync( engine_{f_name}.get( first ) );'
            '}} else {{'
                'engine_{f_name}.search( q, sync );'
            '}}'
        '}}'
        ).format(
                f_name = f_name
        )

def typeahead_updater( f_name ):
    """ The JS script creating the function triggered when an item is
    selected through typeahead """
    return (
        'function(evt, item) {{'
            '$( "#{hidden_id}" ).val( item.key );'
            '$( "#{hidden_id}" ).change();'
            'return item;'
        '}}'
        ).format(
                hidden_id = hidden_id( f_name )
        )

def typeahead_change( f_name ):
    """ The JS script creating the function triggered when an item is changed
    (i.e. looses focus and value has changed since the moment it gained focus
    """
    return (
        'function(evt) {{'
            'if ( $( "#{input_id}" ).typeahead( "val" ) === "" ) {{'
                '$( "#{hidden_id}" ).val( "" );'
                '$( "#{hidden_id}" ).change();'
            '}}'
        '}}'
        ).format(
                input_id = input_id( f_name ),
                hidden_id = hidden_id( f_name )
        )

