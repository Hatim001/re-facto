from typing import Any, Dict

from django.http import HttpRequest, JsonResponse
from django.views.decorators.csrf import csrf_exempt

from core.utils import BaseView
from service.models.github.bot import GithubBot


class GitHubEventListenerService(BaseView):
    """Github event listener service"""

    model = GithubBot

    @csrf_exempt
    def post(self, request: HttpRequest, *args: tuple, **kwargs: dict) -> JsonResponse:
        """
        API for listening events
        :param request: HttpRequest object
        :param args: tuple of arguments
        :param kwargs: dictionary of keyword arguments
        :return: JsonResponse object
        """
        self.model(request=request, is_event=True).process_event()
        response_data: Dict[str, Any] = {"message": "Event processed successfully!"}
        return JsonResponse(response_data, status=200)
