import json

import requests
from django.conf import settings
from django.http import HttpResponse

DEFAULT_HEADERS = {"Content-Type": "application/json"}


def get_request_method(method: str) -> callable:
    """
    Returns the request method based on the input string
    """
    if req_method := {
        "GET": requests.get,
        "PUT": requests.put,
        "POST": requests.post,
        "DELETE": requests.delete,
    }.get(method.upper()):
        return req_method
    else:
        raise ValueError("Invalid request method")


def print_request_failure(
    url: str, response: HttpResponse = None, headers: dict = None, **kwargs: dict
) -> None:
    """
    Prints the details of a failed request
    """
    if headers is None:
        headers = {}
    message = (
        "\n{sep}\n"
        "\033[91m"
        "Python request to url: {url}, failed with status_code: {status_code}"
        "\033[0m"
        "\n{sep}\n"
        "headers: {headers}\n"
        "kwargs: {kwargs}\n"
    ).format(
        url=url,
        sep="-" * 120,
        kwargs=json.dumps(kwargs, indent=2),
        headers=json.dumps(headers, indent=2),
        status_code=response.status_code if response is not None else None,
    )
    print(message)


def fetch(
    url: str,
    method: str = "GET",
    headers: dict = DEFAULT_HEADERS,
    payload: dict = None,
    in_bytes: bool = False,
    parse_json: bool = True,
    should_raise_exception: bool = False,
    **kwargs: dict,
) -> tuple:
    """
    Sends a request to the specified URL using the specified method and headers.
    Returns a tuple containing the status code and response data.

    :param url: The URL to send the request to
    :param method: The HTTP method to use (GET, POST, PUT, DELETE)
    :param headers: The headers to include in the request
    :param payload: The payload to include in the request
    :param in_bytes: Whether to return the response data as bytes or text
    :param parse_json: Whether to parse the response data as JSON
    :param should_raise_exception: Whether to raise an exception if the request fails
    :param kwargs: Additional keyword arguments to pass to the request method
    """
    if payload is None:
        payload = {}
    if not url:
        raise ValueError("Invalid URL")
    elif not isinstance(headers, dict):
        raise TypeError(f"Invalid headers, expected dict got {type(headers)}")

    r: HttpResponse | None = None
    headers: dict = {**DEFAULT_HEADERS, **headers}
    try:
        request_method: callable = get_request_method(method)
        kwargs["params" if method == "GET" else "json"] = payload
        r = request_method(url, headers=headers, **kwargs)
        if not should_raise_exception:
            content = r.content if in_bytes else r.text
            response_data = r.json() if parse_json and not in_bytes else content
            return r.status_code, response_data

        r.raise_for_status()
        content = r.content if in_bytes else r.text
        response_data = r.json() if parse_json and not in_bytes else content
        return r.status_code, response_data
    except Exception as e:
        settings.DEBUG and print_request_failure(
            url, response=r, headers=headers, **kwargs
        )
        raise e