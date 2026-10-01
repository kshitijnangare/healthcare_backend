"""Custom DRF exception handler: every error returns {"success": false, "message", "errors"}."""
import logging

from django.core.exceptions import ObjectDoesNotExist
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import IntegrityError
from django.http import Http404
from rest_framework import status
from rest_framework.exceptions import APIException, ValidationError
from rest_framework.response import Response
from rest_framework.views import exception_handler

logger = logging.getLogger(__name__)


class Conflict(APIException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = "Resource already exists."
    default_code = "conflict"


def _error(message: str, http_status: int, errors=None) -> Response:
    return Response(
        {"success": False, "message": message, "errors": errors or {}},
        status=http_status,
    )


def custom_exception_handler(exc, context):
    if isinstance(exc, (Http404, ObjectDoesNotExist)):
        return _error("Resource not found.", status.HTTP_404_NOT_FOUND)

    if isinstance(exc, IntegrityError):
        logger.warning("IntegrityError: %s", exc)
        return _error(
            "A database constraint was violated (duplicate or invalid reference).",
            status.HTTP_409_CONFLICT,
        )

    if isinstance(exc, DjangoValidationError):
        exc = ValidationError(detail=exc.message_dict if hasattr(exc, "error_dict") else exc.messages)

    response = exception_handler(exc, context)

    if response is None:  # unhandled exception -> never leak a stack trace
        logger.exception("Unhandled exception", exc_info=exc)
        return _error("Internal server error.", status.HTTP_500_INTERNAL_SERVER_ERROR)

    if isinstance(exc, ValidationError):
        return _error("Validation failed.", response.status_code, response.data)

    data = response.data
    message = data.get("detail") if isinstance(data, dict) else None
    return _error(str(message or "Request failed."), response.status_code)
