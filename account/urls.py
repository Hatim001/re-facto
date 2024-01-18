from django.urls import include, path

from account.views.github.auth import GithubAuthorizationView
from account.views.github.config import GitHubConfigurationView
from account.views.github.dash_info import GithubDashboardView

github_urlpatterns = [
    path("authorize/", GithubAuthorizationView.as_view()),
    path("configurations/", GitHubConfigurationView.as_view()),
]

urlpatterns = [
    path("github/", include(github_urlpatterns)),
    path("session/", GithubAuthorizationView.as_view()),
    path("logout/", GithubAuthorizationView.as_view()),
    path("dashboard/home/", GithubDashboardView.as_view()),
]
