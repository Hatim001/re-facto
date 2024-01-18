from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.renderers import JSONRenderer

from account.proxies.dashboard_fetch import DashBoardFetch
from core.utils.base_view import BaseView


class GithubDashboardView(BaseView):
    model = DashBoardFetch

    @csrf_exempt
    def post(self, request, *args, **kwargs):
        data = self.model.fetch_dashboard_data(request=request)
        return JsonResponse(data=data, status=200)
