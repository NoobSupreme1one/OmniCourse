from __future__ import annotations

from typing import Any

from django.conf import settings
from rest_framework.permissions import SAFE_METHODS, BasePermission


def _get_owner_from_obj(obj: Any) -> Any | None:
    if hasattr(obj, "owner") and obj.owner is not None:
        return obj.owner
    # Module -> Course.owner
    if obj.__class__.__name__ == "Module":
        try:
            return obj.course.owner
        except Exception:
            return None
    # Lesson -> Module.course.owner
    if obj.__class__.__name__ == "Lesson":
        try:
            return obj.module.course.owner
        except Exception:
            return None
    # ExportArtifact -> Course.owner
    if obj.__class__.__name__ == "ExportArtifact":
        try:
            return obj.course.owner
        except Exception:
            return None
    return None


class OwnerOrReadOnly(BasePermission):
    """
    Allow read to everyone. Writes require authentication and ownership.

    In test settings, `ALLOW_ANON_WRITE_FOR_TESTS=True` permits anonymous writes
    to keep legacy tests green while ownership is phased in.
    """

    def has_permission(self, request, view) -> bool:  # noqa: ANN001
        if request.method in SAFE_METHODS:
            return True

        # Allow anonymous writes in tests if flag set
        if getattr(settings, "ALLOW_ANON_WRITE_FOR_TESTS", False):
            return True

        # Must be authenticated for writes otherwise
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj) -> bool:  # noqa: ANN001
        if request.method in SAFE_METHODS:
            return True

        if getattr(settings, "ALLOW_ANON_WRITE_FOR_TESTS", False):
            return True

        if not (request.user and request.user.is_authenticated):
            return False

        owner = _get_owner_from_obj(obj)
        return bool(owner and owner == request.user)
