"""Afvalcontainers URL Configuration.

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
from django.conf import settings
from django.conf.urls import url, include

from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from rest_framework import routers
from rest_framework import permissions

from . import views as api_views
from kilogram import views as kilo_views


class ContainersView(routers.APIRootView):
    """
    Garbadge Containers in the city are show here as list.

    It is possible to filter the list

    Model Overview
    ==================

    Type ->  Container ->  Well ->  Site

    A site is a collection of wells. Each well can contain
    a container. The container and type in a well can change.

    Daily Import Overview
    =====================

     1. Scrape Bammens API ~12.500 wells/containers
     2. BGT merge ~8500 wells merged with BGT (8-2018)
     3. Cleanup ,
     4. Fills site endpoint for route planning/ dashboards
     5. Publish API / Geo services

    [github/amsterdam/afvalcontainers](https://github.com/Amsterdam/afvalcontainers)

    [Author: s.preeker](https://github.com/spreeker/)
    """


class ContainerRouter(routers.DefaultRouter):
    APIRootView = ContainersView


containers = ContainerRouter()

containers.register(
    r"containers", api_views.ContainerView, base_name="container")
containers.register(
    r"wells", api_views.WellView, base_name="well")
containers.register(
    r"containertypes", api_views.TypeView, base_name="containertype")

# LIVE KILOGRAM DATABASE UPDATES
containers.register(
    r"sites", api_views.SiteView, base_name="site")
containers.register(
    r"kilogram", kilo_views.KilogramView, base_name="kilogram")


# stats views
containers.register(
    r'kilos/sites/weekly',
    kilo_views.WeighDataSiteWeekView, base_name='stats-site-week')

containers.register(
    r'kilos/sites/monthly',
    kilo_views.WeighDataSiteMonthView, base_name='stats-site-month')

containers.register(
    r'kilos/neighborhood/weekly',
    kilo_views.WeighDataBuurtWeekView, base_name='stats-site-week')

containers.register(
    r'kilos/neighborhood/monthly',
    kilo_views.WeighDataBuurtMonthView, base_name='stats-site-month')


# containers.register(r"stats", stats, base_name='stats')


urls = containers.urls

schema_view = get_schema_view(
    openapi.Info(
        title="Afval Container API",
        default_version='v1',
        description="Afvalcontainers en Wells in Amsterdam",
        terms_of_service="https://data.amsterdam.nl/",
        contact=openapi.Contact(email="datapunt@amsterdam.nl"),
        license=openapi.License(name="CC0 1.0 Universal"),
    ),
    validators=['flex', 'ssv'],
    public=True,
    permission_classes=(permissions.AllowAny,),
)


urlpatterns = [
    # url(r"^afval/stats/", include(stats.urls)),

    url(r'^afval/swagger(?P<format>\.json|\.yaml)$',
        schema_view.without_ui(cache_timeout=None), name='schema-json'),
    url(r'^afval/swagger/$',
        schema_view.with_ui('swagger', cache_timeout=None),
        name='schema-swagger-ui'),
    url(r'^afval/redoc/$',
        schema_view.with_ui('redoc', cache_timeout=None), name='schema-redoc'),
    url(r"^afval/", include(urls)),
    url(r"^status/", include("afvalcontainers.health.urls")),

]


if settings.DEBUG:
    import debug_toolbar

    urlpatterns.extend([
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ])
