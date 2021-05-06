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
from enevo import views as enevo_views
from sidcon import views as sidcon_views

from afvalcontainers.routers import AfvalContainerAPIRootView
from afvalcontainers.routers import SupliersAPIRootView

from afvalcontainers.v1.routers import AfvalContainerAPIRootViewVersion1

from django.urls import path


class MainRouter(routers.DefaultRouter):
    APIRootView = AfvalContainerAPIRootView


class SuppliersRouter(routers.DefaultRouter):
    APIRootView = SupliersAPIRootView


class V1Router(routers.DefaultRouter):
    APIRootView = AfvalContainerAPIRootViewVersion1


afvalroot = MainRouter()

afval_v1 = V1Router()

suppliers = SuppliersRouter()


afval_v1.register(
    r"containers", api_views.ContainerView, basename="container")
afval_v1.register(
    r"wells", api_views.WellView, basename="well")
afval_v1.register(
    r"containertypes", api_views.TypeView, basename="containertype")

afval_v1.register(
    r"sites", api_views.SiteView, basename="site")
afval_v1.register(
    r"sitefracties", api_views.SiteFractieView, basename="sitefractie")

# LIVE KILOGRAM DATABASE UPDATES
suppliers.register(
    r"kilogram", kilo_views.KilogramView, basename="kilogram")

# stats views
# supplies.register(
#     r'kilos/sites/weekly',
#     kilo_views.WeighDataSiteWeekView, basename='stats-site-week')
#
# containers.register(
#     r'kilos/sites/monthly',
#     kilo_views.WeighDataSiteMonthView, basename='stats-site-month')
#
# containers.register(
#     r'kilos/neighborhood/weekly',
#     kilo_views.WeighDataBuurtWeekView, basename='stats-wijk-week')
#
# containers.register(
#     r'kilos/neighborhood/monthly',
#     kilo_views.WeighDataBuurtMonthView, basename='stats-wijk-month')


suppliers.register(
    r'enevo/containers',
    enevo_views.ContainerView, basename='enevocontainer')

suppliers.register(
    r'enevo/containertypes',
    enevo_views.ContainerTypeView, basename='enevocontainertype')

suppliers.register(
    r'enevo/sites',
    enevo_views.SiteView, basename='enevosite')

suppliers.register(
    r'enevo/sitecontenttypes',
    enevo_views.SiteContentTypeView, basename='enevositecontenttype')

suppliers.register(
    r'enevo/containerslots',
    enevo_views.ContainerSlotView, basename='enevocontainerslot')

suppliers.register(
    r'enevo/alerts',
    enevo_views.AlertView, basename='enevoalert')

suppliers.register(
    r'enevo/contenttypes',
    enevo_views.ContentTypeView, basename='enevocontenttype')
# containers.register(r"stats", stats, basename='stats')
suppliers.register(
    r'enevo/filllevels',
    enevo_views.FillLevelView, basename='enevofilllevel')

suppliers.register(
    r'sidcon/filllevels',
    sidcon_views.SidconView, basename='sidconfilllevel')


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

urls = afvalroot.urls

urlpatterns = [
    # url(r"^afval/stats/", include(stats.urls)),

    url(r'^afval/swagger(?P<format>\.json|\.yaml)$',
        schema_view.without_ui(cache_timeout=None), name='schema-json'),
    url(r'^afval/swagger/$',
        schema_view.with_ui('swagger', cache_timeout=None),
        name='schema-swagger-ui'),
    url(r'^afval/redoc/$',
        schema_view.with_ui('redoc', cache_timeout=None), name='schema-redoc'),
    url(r'^status/', include("afvalcontainers.health.urls")),

    # supplier urls
    url(r'^afval/suppliers/',
        include((suppliers.urls, 'suppliers'), namespace='suppliers')),

    # API Version 1
    url(r'^afval/v1/', include((afval_v1.urls, 'v1'), namespace='v1')),

    url(r'^afval/', include(urls)),

]


if settings.DEBUG:
    import debug_toolbar

    urlpatterns.extend([
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ])
