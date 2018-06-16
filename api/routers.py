# Re2o est un logiciel d'administration développé initiallement au rezometz. Il
# se veut agnostique au réseau considéré, de manière à être installable en
# quelques clics.
#
# Copyright © 2018  Mael Kervella
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
"""api.routers

Definition of the custom routers to generate the URLs of the API
"""

from collections import OrderedDict
from django.conf.urls import url, include
from django.core.urlresolvers import NoReverseMatch
from rest_framework import views
from rest_framework.routers import DefaultRouter
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.schemas import SchemaGenerator
from rest_framework.settings import api_settings

class AllViewsRouter(DefaultRouter):
    def __init__(self, *args, **kwargs):
        self.view_registry = []
        super(AllViewsRouter, self).__init__(*args, **kwargs)

    def register_viewset(self, *args, **kwargs):
        """
        Register a viewset in the router
        Alias of `register` for convenience
        """
        return self.register(*args, **kwargs)

    def register_view(self, pattern, view, name=None):
        """
        Register a view in the router
        """
        if name is None:
            name = self.get_default_name(pattern)
        self.view_registry.append((pattern, view, name))

    def get_default_name(self, pattern):
        return pattern.split('/')[-1]

    def get_api_root_view(self, schema_urls=None):
        """
        Return a view to use as the API root.
        """
        api_root_dict = OrderedDict()
        list_name = self.routes[0].name
        for prefix, viewset, basename in self.registry:
            api_root_dict[prefix] = list_name.format(basename=basename)
        for pattern, view, name in self.view_registry:
            api_root_dict[pattern] = name

        view_renderers = list(api_settings.DEFAULT_RENDERER_CLASSES)
        schema_media_types = []

        if schema_urls and self.schema_title:
            view_renderers += list(self.schema_renderers)
            schema_generator = SchemaGenerator(
                title=self.schema_title,
                patterns=schema_urls
            )
            schema_media_types = [
                renderer.media_type
                for renderer in self.schema_renderers
            ]

        class APIRoot(views.APIView):
            _ignore_model_permissions = True
            renderer_classes = view_renderers

            def get(self, request, *args, **kwargs):
                if request.accepted_renderer.media_type in schema_media_types:
                    # Return a schema response.
                    schema = schema_generator.get_schema(request)
                    if schema is None:
                        raise exceptions.PermissionDenied()
                    return Response(schema)

                # Return a plain {"name": "hyperlink"} response.
                ret = OrderedDict()
                namespace = request.resolver_match.namespace
                for key, url_name in api_root_dict.items():
                    if namespace:
                        url_name = namespace + ':' + url_name
                    try:
                        ret[key] = reverse(
                            url_name,
                            args=args,
                            kwargs=kwargs,
                            request=request,
                            format=kwargs.get('format', None)
                        )
                    except NoReverseMatch:
                        # Don't bail out if eg. no list routes exist, only detail routes.
                        continue

                return Response(ret)

        return APIRoot.as_view()

    def get_urls(self):
        urls = super(AllViewsRouter, self).get_urls()

        for pattern, view, name in self.view_registry:
            urls.append(url(pattern, view.as_view(), name=name))

        return urls
