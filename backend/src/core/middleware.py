"""
Custom middleware for OmniCourse project.
"""

import hashlib
import json
from datetime import timedelta

from django.core.cache import cache
from django.http import JsonResponse
from django.utils import timezone

try:
    from jobs.models import IdempotencyKey  # Local import to avoid early model import
except Exception:  # pragma: no cover - safe fallback if migrations not ready
    IdempotencyKey = None  # type: ignore


class IdempotencyKeyMiddleware:
    """
    Middleware to handle idempotency keys for POST requests.

    Stores request hash and response for a period to prevent duplicate processing.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Only apply to POST requests with idempotency key
        if (
            request.method == "POST"
            and "Idempotency-Key" in request.headers
            and request.path.startswith("/api/")
        ):

            idempotency_key = request.headers["Idempotency-Key"]
            request_hash = self._get_request_hash(request, idempotency_key)

            # Check if we've seen this request before (cache first)
            cached_response = cache.get(f"idempotent:{request_hash}")
            if cached_response:
                resp = JsonResponse(
                    cached_response["data"], status=cached_response["status"]
                )
                return resp

            # Check persistent storage as fallback
            if IdempotencyKey is not None:
                try:
                    record = IdempotencyKey.objects.filter(
                        key=idempotency_key, request_hash=request_hash, expires_at__gt=timezone.now()
                    ).order_by("-created_at").first()
                    if record is not None:
                        resp = JsonResponse(record.response_data, status=record.response_status)
                        cache.set(
                            f"idempotent:{request_hash}",
                            {"data": record.response_data, "status": record.response_status},
                            timeout=3600,
                        )
                        return resp
                except Exception:
                    # Fail open: proceed with the request if DB not ready
                    pass

        response = self.get_response(request)

        # Cache and persist successful responses for idempotency
        if hasattr(request, "idempotency_key") and 200 <= response.status_code < 300:
            try:
                response_data = json.loads(response.content)

                # Cache
                cache.set(
                    f"idempotent:{request.idempotency_hash}",
                    {"data": response_data, "status": response.status_code},
                    timeout=3600,  # 1 hour
                )

                # Persist to DB for replay across workers/restarts
                if IdempotencyKey is not None:
                    try:
                        IdempotencyKey.objects.update_or_create(
                            key=request.idempotency_key,
                            request_hash=request.idempotency_hash,
                            defaults={
                                "response_data": response_data,
                                "response_status": response.status_code,
                                "expires_at": timezone.now() + timedelta(hours=1),
                            },
                        )
                    except Exception:
                        # Ignore persistence failure; cache still holds it
                        pass
            except (json.JSONDecodeError, AttributeError):
                pass

        return response

    def _get_request_hash(self, request, idempotency_key):
        """Create hash of request for idempotency checking."""
        hash_input = f"{request.path}:{idempotency_key}:{request.body.decode()}"
        request_hash = hashlib.sha256(hash_input.encode()).hexdigest()

        # Store on request for later use
        request.idempotency_key = idempotency_key
        request.idempotency_hash = request_hash

        return request_hash
