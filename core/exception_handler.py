import logging

from django.core.exceptions import PermissionDenied, ValidationError
from django.http import Http404
from rest_framework import exceptions
from rest_framework.views import exception_handler

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    # Map Django core exceptions to DRF equivalents
    if isinstance(exc, Http404):
        exc = exceptions.NotFound()
    elif isinstance(exc, PermissionDenied):
        exc = exceptions.PermissionDenied()
    elif isinstance(exc, ValidationError):
        exc = exceptions.ValidationError(
            detail=exc.message_dict if hasattr(exc, "message_dict") else exc.messages
        )

    response = exception_handler(exc, context)

    if response is not None:
        code = response.status_code

        # Flatten DRF error detail into a single string
        detail = response.data.get("detail", None)
        if detail is not None:
            error = str(detail)
        else:
            # Validation errors: {"field": ["msg"]} → join all messages
            messages = []
            for field, value in response.data.items():
                if isinstance(value, list):
                    for item in value:
                        messages.append(f"{field}: {item}")
                else:
                    messages.append(f"{field}: {value}")
            error = "; ".join(messages) if messages else "An error occurred."

        response.data = {"error": error, "code": code}

        if code >= 500:
            logger.error("Server error %s – %s", code, error, exc_info=exc)
        elif code >= 400:
            logger.warning("Client error %s – %s", code, error)

    return response
