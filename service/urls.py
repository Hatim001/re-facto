from typing import List

from django.urls import include, path

from service.views.github.event import GitHubEventListenerService


def get_github_patterns() -> List[path]:
    """
    Returns a list of URL patterns for the GitHub API endpoints.
    """
    return [path("event/", GitHubEventListenerService.as_view(), name="github_event")]


urlpatterns = [path("github/", include(get_github_patterns()))]
