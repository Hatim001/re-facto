from django.http import QueryDict
from rest_framework.views import APIView

from core.utils.exceptions import ValidationError


class BaseView(APIView):
    """
    Base View for all the API's.
    Consists of some common utils based on request
    """

    def parse_payload(self, request):
        """
        Parses the payload from the request object.

        Args:
            request (Request): The request object.

        Returns:
            dict: The parsed payload.
        """
        return (
            request.data.dict() if isinstance(request.data, QueryDict) else request.data
        )

    def validate_instance(self, instance):
        """
        Validates the instance and raises a ValidationError if it is invalid.

        Args:
            instance: The instance to validate.

        Raises:
            ValidationError: If the instance is invalid.
        """
        if not instance:
            raise ValidationError("Invalid instance.")
