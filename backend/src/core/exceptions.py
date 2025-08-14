"""
Custom DRF exception handler returning RFC 7807 Problem+JSON responses.
"""

from __future__ import annotations

from typing import Any

from django.http import JsonResponse
from django.utils.translation import gettext as _
from rest_framework import status
from rest_framework.views import exception_handler as drf_exception_handler


def problem_exception_handler(exc: Exception, context: dict[str, Any]) -> JsonResponse | Any:
    """
    Wrap DRF's default handler to emit Problem+JSON (RFC 7807) shapes consistently.
    """
    response = drf_exception_handler(exc, context)
    if response is None:
        # Non-DRF exception; return generic 500 Problem
        return _problem(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            title=_("Internal Server Error"),
            detail=str(exc),
            type_="about:blank",
        )

    # DRF built a response (contains .data and .status_code)
    detail = None
    errors = None

    data = getattr(response, "data", {}) or {}
    if isinstance(data, dict):
        # Normalize DRF structure into detail + errors
        if "detail" in data and len(data) == 1:
            detail = data.get("detail")
        else:
            errors = data
    else:
        # Non-dict data becomes detail
        detail = str(data)

    title = _default_title_for_status(response.status_code)
    return _problem(
        status_code=response.status_code,
        title=title,
        detail=detail,
        type_="about:blank",
        errors=errors,
    )


def _problem(
    *,
    status_code: int,
    title: str,
    detail: str | None = None,
    type_: str = "about:blank",
    instance: str | None = None,
    errors: dict[str, Any] | None = None,
) -> JsonResponse:
    payload: dict[str, Any] = {
        "type": type_,
        "title": title,
        "status": status_code,
    }
    if detail:
        payload["detail"] = detail
    if instance:
        payload["instance"] = instance
    if errors:
        payload["errors"] = errors

    resp = JsonResponse(payload, status=status_code)
    resp["Content-Type"] = "application/problem+json"
    return resp


def _default_title_for_status(code: int) -> str:
    mapping = {
        400: _("Bad Request"),
        401: _("Unauthorized"),
        403: _("Forbidden"),
        404: _("Not Found"),
        405: _("Method Not Allowed"),
        409: _("Conflict"),
        415: _("Unsupported Media Type"),
        422: _("Unprocessable Entity"),
        429: _("Too Many Requests"),
        500: _("Internal Server Error"),
        502: _("Bad Gateway"),
        503: _("Service Unavailable"),
    }
    return mapping.get(code, _("Error"))
