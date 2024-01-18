import contextlib
import traceback

from django.conf import settings
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin


class ErrorReportingMiddleware(MiddlewareMixin):
    """
    Middleware to capture errors and process
    """

    def validate_status_code(self, status_code):
        """
        Check if status code is correct or not
        """
        if isinstance(status_code, int):
            return status_code

        with contextlib.suppress(Exception):
            return int(status_code)
        return 500

    def print_traceback(self, error, has_message=False):
        """
        Format the traceback and print it on the console for easier debugging
        """
        traceback_str = traceback.format_exc()
        to_print = (
            "\033[91m"
            "\n{sep}\n"
            "{message}\n"
            "{sep}\n"
            "{traceback}\n"
            "{sep}\n"
            "\033[0m"
        )
        print(
            to_print.format(
                sep="-" * 100,
                traceback=traceback_str,
                message=error.message if has_message else str(error),
            )
        )
        return traceback_str

    def report_exception(self, request, exception):
        """
        Report exception
        """
        has_message = hasattr(exception, "message")
        has_status_code = hasattr(exception, "status_code")
        status_code = exception.status_code if has_status_code else 500
        if has_message and isinstance(exception.message, Exception):
            exception = exception.message

        response = {"message": exception.message if has_message else str(exception)}
        if settings.DEBUG:
            response["traceback"] = self.print_traceback(
                exception, has_message=has_message
            )
            return self.validate_status_code(status_code), response

        return self.validate_status_code(status_code), response

    def process_exception(self, request, error):
        """
        Catch all the exceptions and return the HttpResponse
        with appropriate status_code
        """
        status_code, response = self.report_exception(request, error)
        return JsonResponse(response, status=status_code or 500)
