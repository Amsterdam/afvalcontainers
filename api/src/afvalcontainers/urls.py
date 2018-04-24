"""Parkeervakken URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from rest_framework import response, schemas
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.renderers import CoreJSONRenderer

from rest_framework import routers

from . import views as api_views


class ContainersView(routers.APIRootView):
    """
    Garbadge Containers in the city are show here as list.
    It is possible to filter the list
    """


class ContainerRouter(routers.DefaultRouter):
    APIRootView = ContainersView


containers = ContainerRouter()
containers.register(r"containers", api_views.ContainerView, base_name="container")
containers.register(r"wells", api_views.WellView, base_name="well")
containers.register(r"containertypes", api_views.TypeView, base_name="containertype")

urls = containers.urls

urlpatterns = [
    url(r"^afval/", include(urls)),
    url(r"^status/", include("afvalcontainers.health.urls")),
]


@api_view()
@renderer_classes([CoreJSONRenderer])
def afval_schema_view(request):
    generator = schemas.SchemaGenerator(title="Geo Endpoints", patterns=urlpatterns)
    return response.Response(generator.get_schema(request=request))
