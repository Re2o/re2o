# -*- mode: python; coding: utf-8 -*-
# Re2o est un logiciel d'administration développé initiallement au Rézo Metz. Il
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

""" Templatetag used to render massive django form selects into bootstrap
forms that can still be manipulating even if there is multiple tens of
thousands of elements in the select. It's made possible using JS libaries
Twitter Typeahead and Splitree's Tokenfield.
See docstring of massive_bootstrap_form for a detailed explaantion on how
to use this templatetag.
"""

from django import template
from django.utils.safestring import mark_safe
from django.forms import TextInput
from django.forms.widgets import Select
from django.utils.translation import ugettext_lazy as _
from bootstrap3.utils import render_tag
from bootstrap3.forms import render_field

register = template.Library()


@register.simple_tag
def massive_bootstrap_form(form, mbf_fields, *args, **kwargs):
    """
    Render a form where some specific fields are rendered using Twitter
    Typeahead and/or splitree's Bootstrap Tokenfield to improve the
    performance, the speed and UX when dealing with very large datasets
    (select with 50k+ elts for instance).
    When the fields specified should normally be rendered as a select with
    single selectable option, Twitter Typeahead is used for a better display
    and the matching query engine. When dealing with multiple selectable
    options, sliptree's Bootstrap Tokenfield in addition with Typeahead.
    For convenience, it accepts the same parameters as a standard bootstrap
    can accept.

    **Tag name**::

        massive_bootstrap_form

    **Parameters**:

        form (required)
            The form that is to be rendered

        mbf_fields (optional)
            A list of field names (comma separated) that should be rendered
            with Typeahead/Tokenfield instead of the default bootstrap
            renderer.
            If not specified, all fields will be rendered as a normal bootstrap
            field.

        mbf_param (optional)
            A dict of parameters for the massive_bootstrap_form tag. The
            possible parameters are the following.

            choices (optional)
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

            engine (optional)
                A dict of strings representating the engine used for matching
                queries and possible values with typeahead. The keys of the
                dict are the names of the concerned fields. The string is valid
                JS code.
                If not specified, BloodHound with relevant basic properties is
                used.
                Example :
                'engine' : {'field_A': 'new Bloodhound()', 'field_B': ..., ...}

            match_func (optional)
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

            update_on (optional)
                A dict of list of ids that the values depends on. The engine
                and the typeahead properties are recalculated and reapplied.
                Example :
                'update_on' : {
                 'field_A' : [ 'id0', 'id1', ... ] ,
                 'field_B' : ... ,
                 ...
                }

            gen_select (optional)
                A dict of boolean telling if the form should either generate
                the normal select (set to true) and then use it to generate
                the possible choices and then remove it or either (set to
                false) generate the choices variable in this tag and do not
                send any select.
                Sending the select before can be usefull to permit the use
                without any JS enabled but it will execute more code locally
                for the client so the loading might be slower.
                If not specified, this variable is set to true for each field
                Example :
                'gen_select' : {
                 'field_A': True ,
                 'field_B': ... ,
                 ...
                }

        See boostrap_form_ for other arguments

    **Usage**::

        {% massive_bootstrap_form
            form
            [ '<field1>[,<field2>[,...]]' ]
            [ mbf_param = {
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
                } ],
                [, 'gen_select': {
                    [  '<field1>': '<gen_select1>'
                    [, '<field2>': '<gen_select2>'
                    [, ... ] ] ]
                } ]
            } ]
            [ <standard boostrap_form parameters> ]
        %}

    **Example**:

        {% massive_bootstrap_form form 'ipv4' choices='[...]' %}
    """

    mbf_form = MBFForm(form, mbf_fields.split(","), *args, **kwargs)
    return mbf_form.render()


class MBFForm:
    """ An object to hold all the information and useful methods needed to
    create and render a massive django form into an actual HTML and JS
    code able to handle it correctly.
    Every field that is not listed is rendered as a normal bootstrap_field.
    """

    def __init__(self, form, mbf_fields, *args, **kwargs):
        # The django form object
        self.form = form
        # The fields on which to use JS
        self.fields = mbf_fields

        # Other bootstrap_form arguments to render the fields
        self.args = args
        self.kwargs = kwargs

        # Fields to exclude form the form rendering
        self.exclude = self.kwargs.get("exclude", "").split(",")

        # All the mbf parameters specified byt the user
        param = kwargs.pop("mbf_param", {})
        self.choices = param.get("choices", {})
        self.engine = param.get("engine", {})
        self.match_func = param.get("match_func", {})
        self.update_on = param.get("update_on", {})
        self.gen_select = param.get("gen_select", {})
        self.hidden_fields = [h.name for h in self.form.hidden_fields()]

        # HTML code to insert inside a template
        self.html = ""

    def render(self):
        """ HTML code for the fully rendered form with all the necessary form
        """
        for name, field in self.form.fields.items():
            if name not in self.exclude:

                if name in self.fields and name not in self.hidden_fields:
                    mbf_field = MBFField(
                        name,
                        field,
                        field.get_bound_field(self.form, name),
                        self.choices.get(name, None),
                        self.engine.get(name, None),
                        self.match_func.get(name, None),
                        self.update_on.get(name, None),
                        self.gen_select.get(name, True),
                        *self.args,
                        **self.kwargs
                    )
                    self.html += mbf_field.render()

                else:
                    f = field.get_bound_field(self.form, name), self.args, self.kwargs
                    self.html += render_field(
                        field.get_bound_field(self.form, name),
                        *self.args,
                        **self.kwargs
                    )

        return mark_safe(self.html)


class MBFField:
    """ An object to hold all the information and useful methods needed to
    create and render a massive django form field into an actual HTML and JS
    code able to handle it correctly.
    Twitter Typeahead is used for the display and the matching of queries and
    in case of a MultipleSelect, Sliptree's Tokenfield is also used to manage
    multiple values.
    A div with only non visible elements is created after the div containing
    the displayed input. It's used to store the actual data that will be sent
    to the server """

    def __init__(
        self,
        name_,
        field_,
        bound_,
        choices_,
        engine_,
        match_func_,
        update_on_,
        gen_select_,
        *args_,
        **kwargs_
    ):

        # Verify this field is a Select (or MultipleSelect) (only supported)
        if not isinstance(field_.widget, Select):
            raise ValueError(
                (
                    "Field named {f_name} is not a Select and"
                    "can't be rendered with massive_bootstrap_form."
                ).format(f_name=name_)
            )

        # Name of the field
        self.name = name_
        # Django field object
        self.field = field_
        # Bound Django field associated with field
        self.bound = bound_

        # Id for the main visible input
        self.input_id = self.bound.auto_id
        # Id for a hidden input used to store the value
        self.hidden_id = self.input_id + "_hidden"
        # Id for another div containing hidden inputs and script
        self.div2_id = self.input_id + "_div"

        # Should the standard select should be generated
        self.gen_select = gen_select_
        # Is it select with multiple values possible (use of tokenfield)
        self.multiple = self.field.widget.allow_multiple_selected
        # JS for the choices variable (user specified or default)
        self.choices = choices_ or self.default_choices()
        # JS for the engine variable (typeahead) (user specified or default)
        self.engine = engine_ or self.default_engine()
        # JS for the matching function (typeahead) (user specified or default)
        self.match_func = match_func_ or self.default_match_func()
        # JS for the datasets variable (typeahead) (user specified or default)
        self.datasets = self.default_datasets()
        # Ids of other fields to bind a reset/reload with when changed
        self.update_on = update_on_ or []

        # Whole HTML code to insert in the template
        self.html = ""
        # JS code in the script tag
        self.js_script = ""
        # Input tag to display instead of select
        self.replace_input = None

        # Other bootstrap_form arguments to render the fields
        self.args = args_
        self.kwargs = kwargs_

    def default_choices(self):
        """ JS code of the variable choices_<fieldname> """

        if self.gen_select:
            return (
                "function plop(o) {{"
                "var c = [];"
                "for( let i=0 ; i<o.length ; i++) {{"
                "    c.push( {{ key: o[i].value, value: o[i].text }} );"
                "}}"
                "return c;"
                '}} ($("#{select_id}")[0].options)'
            ).format(select_id=self.input_id)

        else:
            return "[{objects}]".format(
                objects=",".join(
                    [
                        '{{key:{k},value:"{v}"}}'.format(
                            k=choice[0] if choice[0] != "" else '""', v=choice[1]
                        )
                        for choice in self.field.choices
                    ]
                )
            )

    def default_engine(self):
        """ Default JS code of the variable engine_<field_name> """
        return (
            "new Bloodhound({{"
            '    datumTokenizer: Bloodhound.tokenizers.obj.whitespace("value"),'
            "    queryTokenizer: Bloodhound.tokenizers.whitespace,"
            "    local: choices_{name},"
            "    identify: function(obj) {{ return obj.key; }}"
            "}})"
        ).format(name=self.name)

    def default_datasets(self):
        """ Default JS script of the datasets to use with typeahead """
        return (
            "{{"
            "    hint: true,"
            "    highlight: true,"
            "    minLength: 0"
            "}},"
            "{{"
            '    display: "value",'
            '    name: "{name}",'
            "    source: {match_func}"
            "}}"
        ).format(name=self.name, match_func=self.match_func)

    def default_match_func(self):
        """ Default JS code of the matching function to use with typeahed """
        return (
            "function ( q, sync ) {{"
            '    if ( q === "" ) {{'
            "        var first = choices_{name}.slice( 0, 5 ).map("
            "            function ( obj ) {{ return obj.key; }}"
            "        );"
            "        sync( engine_{name}.get( first ) );"
            "    }} else {{"
            "        engine_{name}.search( q, sync );"
            "    }}"
            "}}"
        ).format(name=self.name)

    def render(self):
        """ HTML code for the fully rendered field """
        self.gen_displayed_div()
        self.gen_hidden_div()
        return mark_safe(self.html)

    def gen_displayed_div(self):
        """ Generate HTML code for the div that contains displayed tags """
        if self.gen_select:
            self.html += render_field(self.bound, *self.args, **self.kwargs)

        self.field.widget = TextInput(
            attrs={
                "name": "mbf_" + self.name,
                "placeholder": getattr(self.field, "empty_label", _("Nothing")),
            }
        )
        self.replace_input = render_field(self.bound, *self.args, **self.kwargs)

        if not self.gen_select:
            self.html += self.replace_input

    def gen_hidden_div(self):
        """ Generate HTML code for the div that contains hidden tags """
        self.gen_full_js()

        content = self.js_script
        if not self.multiple and not self.gen_select:
            content += self.hidden_input()

        self.html += render_tag("div", content=content, attrs={"id": self.div2_id})

    def hidden_input(self):
        """ HTML for the hidden input element """
        return render_tag(
            "input",
            attrs={
                "id": self.hidden_id,
                "name": self.bound.html_name,
                "type": "hidden",
                "value": self.bound.value() or "",
            },
        )

    def gen_full_js(self):
        """ Generate the full script tag containing the JS code """
        self.create_js()
        self.fill_js()
        self.get_script()

    def create_js(self):
        """ Generate a template for the whole script to use depending on
        gen_select and multiple """
        if self.gen_select:
            if self.multiple:
                self.js_script = (
                    '$( "#{input_id}" ).ready( function() {{'
                    "    var choices_{f_name} = {choices};"
                    "    {del_select}"
                    "    var engine_{f_name};"
                    "    var setup_{f_name} = function() {{"
                    "        engine_{f_name} = {engine};"
                    '        $( "#{input_id}" ).tokenfield( "destroy" );'
                    '        $( "#{input_id}" ).tokenfield({{typeahead: [ {datasets} ] }});'
                    "    }};"
                    '    $( "#{input_id}" ).bind( "tokenfield:createtoken", {tok_create} );'
                    '    $( "#{input_id}" ).bind( "tokenfield:edittoken", {tok_edit} );'
                    '    $( "#{input_id}" ).bind( "tokenfield:removetoken", {tok_remove} );'
                    "    {tok_updates}"
                    "    setup_{f_name}();"
                    "    {tok_init_input}"
                    "}} );"
                )
            else:
                self.js_script = (
                    '$( "#{input_id}" ).ready( function() {{'
                    "    var choices_{f_name} = {choices};"
                    "    {del_select}"
                    "    {gen_hidden}"
                    "    var engine_{f_name};"
                    "    var setup_{f_name} = function() {{"
                    "        engine_{f_name} = {engine};"
                    '        $( "#{input_id}" ).typeahead( "destroy" );'
                    '        $( "#{input_id}" ).typeahead( {datasets} );'
                    "    }};"
                    '    $( "#{input_id}" ).bind( "typeahead:select", {typ_select} );'
                    '    $( "#{input_id}" ).bind( "typeahead:change", {typ_change} );'
                    "    {typ_updates}"
                    "    setup_{f_name}();"
                    "    {typ_init_input}"
                    "}} );"
                )
        else:
            if self.multiple:
                self.js_script = (
                    "var choices_{f_name} = {choices};"
                    "var engine_{f_name};"
                    "var setup_{f_name} = function() {{"
                    "    engine_{f_name} = {engine};"
                    '    $( "#{input_id}" ).tokenfield( "destroy" );'
                    '    $( "#{input_id}" ).tokenfield({{typeahead: [ {datasets} ] }});'
                    "}};"
                    '$( "#{input_id}" ).bind( "tokenfield:createtoken", {tok_create} );'
                    '$( "#{input_id}" ).bind( "tokenfield:edittoken", {tok_edit} );'
                    '$( "#{input_id}" ).bind( "tokenfield:removetoken", {tok_remove} );'
                    "{tok_updates}"
                    '$( "#{input_id}" ).ready( function() {{'
                    "    setup_{f_name}();"
                    "    {tok_init_input}"
                    "}} );"
                )
            else:
                self.js_script = (
                    "var choices_{f_name} ={choices};"
                    "var engine_{f_name};"
                    "var setup_{f_name} = function() {{"
                    "    engine_{f_name} = {engine};"
                    '    $( "#{input_id}" ).typeahead( "destroy" );'
                    '    $( "#{input_id}" ).typeahead( {datasets} );'
                    "}};"
                    '$( "#{input_id}" ).bind( "typeahead:select", {typ_select} );'
                    '$( "#{input_id}" ).bind( "typeahead:change", {typ_change} );'
                    "{typ_updates}"
                    '$( "#{input_id}" ).ready( function() {{'
                    "    setup_{f_name}();"
                    "    {typ_init_input}"
                    "}} );"
                )

        # Make sure the visible element doesn't have the same name as the hidden elements
        # Otherwise, in the POST request, they collide and an incoherent value is sent
        self.js_script += (
            '$( "#{input_id}" ).ready( function() {{'
            '    $( "#{input_id}" ).attr("name", "mbf_{f_name}");'
            "}} );"
        )

    def fill_js(self):
        """ Fill the template with the correct values """
        self.js_script = self.js_script.format(
            f_name=self.name,
            choices=self.choices,
            del_select=self.del_select(),
            gen_hidden=self.gen_hidden(),
            engine=self.engine,
            input_id=self.input_id,
            datasets=self.datasets,
            typ_select=self.typeahead_select(),
            typ_change=self.typeahead_change(),
            tok_create=self.tokenfield_create(),
            tok_edit=self.tokenfield_edit(),
            tok_remove=self.tokenfield_remove(),
            typ_updates=self.typeahead_updates(),
            tok_updates=self.tokenfield_updates(),
            tok_init_input=self.tokenfield_init_input(),
            typ_init_input=self.typeahead_init_input(),
        )

    def get_script(self):
        """ Insert the JS code inside a script tag """
        self.js_script = render_tag("script", content=mark_safe(self.js_script))

    def del_select(self):
        """ JS code to delete the select if it has been generated and replace
        it with an input. """
        return (
            'var p = $("#{select_id}").parent()[0];'
            "var new_input = `{replace_input}`;"
            "p.innerHTML = new_input;"
        ).format(select_id=self.input_id, replace_input=self.replace_input)

    def gen_hidden(self):
        """ JS code to add a hidden tag to store the value. """
        return (
            'var d = $("#{div2_id}")[0];'
            'var i = document.createElement("input");'
            'i.id = "{hidden_id}";'
            'i.name = "{html_name}";'
            'i.value = "";'
            'i.type = "hidden";'
            "d.appendChild(i);"
        ).format(
            div2_id=self.div2_id,
            hidden_id=self.hidden_id,
            html_name=self.bound.html_name,
        )

    def typeahead_init_input(self):
        """ JS code to init the fields values """
        init_key = self.bound.value() or '""'
        return (
            '$( "#{input_id}" ).typeahead("val", {init_val});'
            '$( "#{hidden_id}" ).val( {init_key} );'
        ).format(
            input_id=self.input_id,
            init_val='""'
            if init_key == '""'
            else "engine_{name}.get( {init_key} )[0].value".format(
                name=self.name, init_key=init_key
            ),
            init_key=init_key,
            hidden_id=self.hidden_id,
        )

    def typeahead_reset_input(self):
        """ JS code to reset the fields values """
        return (
            '$( "#{input_id}" ).typeahead("val", "");' '$( "#{hidden_id}" ).val( "" );'
        ).format(input_id=self.input_id, hidden_id=self.hidden_id)

    def typeahead_select(self):
        """ JS code to create the function triggered when an item is selected
        through typeahead """
        return (
            "function(evt, item) {{"
            '    $( "#{hidden_id}" ).val( item.key );'
            '    $( "#{hidden_id}" ).change();'
            "    return item;"
            "}}"
        ).format(hidden_id=self.hidden_id)

    def typeahead_change(self):
        """ JS code of the function triggered when an item is changed (i.e.
        looses focus and value has changed since the moment it gained focus )
        """
        return (
            "function(evt) {{"
            '    if ( $( "#{input_id}" ).typeahead( "val" ) === "" ) {{'
            '        $( "#{hidden_id}" ).val( "" );'
            '        $( "#{hidden_id}" ).change();'
            "    }}"
            "}}"
        ).format(input_id=self.input_id, hidden_id=self.hidden_id)

    def typeahead_updates(self):
        """ JS code for binding external fields changes with a reset """
        reset_input = self.typeahead_reset_input()
        updates = [
            (
                '$( "#{u_id}" ).change( function() {{'
                "    setup_{name}();"
                "    {reset_input}"
                "}} );"
            ).format(u_id=u_id, name=self.name, reset_input=reset_input)
            for u_id in self.update_on
        ]
        return "".join(updates)

    def tokenfield_init_input(self):
        """ JS code to init the fields values """
        init_key = self.bound.value() or '""'
        return ('$( "#{input_id}" ).tokenfield("setTokens", {init_val});').format(
            input_id=self.input_id,
            init_val='""'
            if init_key == '""'
            else (
                "engine_{name}.get( {init_key} ).map("
                "    function(o) {{ return o.value; }}"
                ")"
            ).format(name=self.name, init_key=init_key),
        )

    def tokenfield_reset_input(self):
        """ JS code to reset the fields values """
        return ('$( "#{input_id}" ).tokenfield("setTokens", "");').format(
            input_id=self.input_id
        )

    def tokenfield_create(self):
        """ JS code triggered when a new token is created in tokenfield. """
        return (
            "function(evt) {{"
            "    var k = evt.attrs.key;"
            "    if (!k) {{"
            "        var data = evt.attrs.value;"
            "        var i = 0;"
            "        while ( i<choices_{name}.length &&"
            "                choices_{name}[i].value !== data ) {{"
            "            i++;"
            "        }}"
            "        if ( i === choices_{name}.length ) {{ return false; }}"
            "        k = choices_{name}[i].key;"
            "    }}"
            '    var new_input = document.createElement("input");'
            '    new_input.type = "hidden";'
            '    new_input.id = "{hidden_id}_"+k.toString();'
            "    new_input.value =  k.toString();"
            '    new_input.name = "{html_name}";'
            '    $( "#{div2_id}" ).append(new_input);'
            "}}"
        ).format(
            name=self.name,
            hidden_id=self.hidden_id,
            html_name=self.bound.html_name,
            div2_id=self.div2_id,
        )

    def tokenfield_edit(self):
        """ JS code triggered when a token is edited in tokenfield. """
        return (
            "function(evt) {{"
            "    var k = evt.attrs.key;"
            "    if (!k) {{"
            "        var data = evt.attrs.value;"
            "        var i = 0;"
            "        while ( i<choices_{name}.length &&"
            "                choices_{name}[i].value !== data ) {{"
            "            i++;"
            "        }}"
            "        if ( i === choices_{name}.length ) {{ return true; }}"
            "        k = choices_{name}[i].key;"
            "    }}"
            "    var old_input = document.getElementById("
            '        "{hidden_id}_"+k.toString()'
            "    );"
            "    old_input.parentNode.removeChild(old_input);"
            "}}"
        ).format(name=self.name, hidden_id=self.hidden_id)

    def tokenfield_remove(self):
        """ JS code trigggered when a token is removed from tokenfield. """
        return (
            "function(evt) {{"
            "    var k = evt.attrs.key;"
            "    if (!k) {{"
            "        var data = evt.attrs.value;"
            "        var i = 0;"
            "        while ( i<choices_{name}.length &&"
            "                choices_{name}[i].value !== data ) {{"
            "            i++;"
            "        }}"
            "        if ( i === choices_{name}.length ) {{ return true; }}"
            "        k = choices_{name}[i].key;"
            "    }}"
            "    var old_input = document.getElementById("
            '        "{hidden_id}_"+k.toString()'
            "    );"
            "    old_input.parentNode.removeChild(old_input);"
            "}}"
        ).format(name=self.name, hidden_id=self.hidden_id)

    def tokenfield_updates(self):
        """ JS code for binding external fields changes with a reset """
        reset_input = self.tokenfield_reset_input()
        updates = [
            (
                '$( "#{u_id}" ).change( function() {{'
                "    setup_{name}();"
                "    {reset_input}"
                "}} );"
            ).format(u_id=u_id, name=self.name, reset_input=reset_input)
            for u_id in self.update_on
        ]
        return "".join(updates)
