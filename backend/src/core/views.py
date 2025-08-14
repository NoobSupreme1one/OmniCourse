from django.http import JsonResponse
from django.views import View

from .health import health_payload


class HealthCheckView(View):
    def get(self, request, *args, **kwargs):  # noqa: ARG002
        return JsonResponse(health_payload())
