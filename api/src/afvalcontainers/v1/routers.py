# from django.urls import reverse
from rest_framework import routers

# from afvalcontainers import API_VERSIONS


class AfvalContainerAPIRootViewVersion1(routers.APIRootView):
    """
    Afvalcontainers API endpoints.

    fresh daily cleaned and updated data.
    """

    def get_view_name(self):
        return 'V1'
