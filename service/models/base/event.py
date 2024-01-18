from typing import Optional

from django.http import HttpRequest, QueryDict
from django.http.request import HttpHeaders


class BaseEvent:
    """Base class for git events"""

    def __init__(self, request: HttpRequest) -> None:
        """
        Initializes a BaseEvent object.

        Args:
        - request (HttpRequest): the request object received from the listener
        """
        self.request: HttpRequest = request
        self.headers: HttpHeaders = None
        self.payload: Optional[dict] = None
        self._parse_request()

    def _parse_request(self) -> None:
        """
        Parses the request object and sets the headers and payload attributes.
        """
        self.headers = self.request.headers
        self.payload = (
            self.request.data.dict()
            if isinstance(self.request.data, QueryDict)
            else self.request.data
        )
