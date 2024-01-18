from django.contrib.auth import logout
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.renderers import JSONRenderer

from account.proxies.github_account import GitHubAccount
from core.utils.base_view import BaseView


class GithubAuthorizationView(BaseView):
    model = GitHubAccount

    @csrf_exempt
    def post(self, request, *args, **kwargs):
        """authorizes user and creates account if not exists"""
        payload = self.parse_payload(request=request)
        code = payload.get("code")
        self.model.authorize(oauth_code=code, request=request)
        return JsonResponse(
            data={"message": "Authorization Successful!!"},
            status=200,
            safe=False,
        )

    def get(self, request, *args, **kwargs):
        """returns session if exists"""
        _session = request.session
        return HttpResponse(JSONRenderer().render(_session))

    def delete(self, request, *args, **kwargs):
        """logouts the session"""
        logout(request)
        return JsonResponse({"message": "Logged out successfully!!"})
