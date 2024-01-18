from django.urls import include, path
from rest_framework.documentation import include_docs_urls


def get_app_patterns():
    """
    Returns a list of app patterns.
    """
    return [
        path("account/", include("account.urls")),
        path("service/", include("service.urls")),
    ]


urlpatterns = [
    path("api/", include(get_app_patterns())),
    path("api-docs/", include_docs_urls(title="Re-Facto APIs")),
]
