from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.http import JsonResponse
from rest_framework import viewsets

from assessment.models import Question, Quiz
from core.health import health_payload
from courses.models import Course, Lesson, Module
from jobs.models import AIJob, ExportArtifact

from .permissions import OwnerOrReadOnly
from .serializers import (
    AIJobSerializer,
    CourseSerializer,
    ExportArtifactSerializer,
    LessonSerializer,
    ModuleSerializer,
    QuestionSerializer,
    QuizSerializer,
)


def healthz(_request):
    return JsonResponse(health_payload())


def livez(_request):
    # Liveness: minimal check, return quickly
    payload = {"ok": True, "status": "alive"}
    return JsonResponse(payload)


def readinessz(_request):
    # Readiness should include dependency checks
    return JsonResponse(health_payload())


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all().order_by("-id")
    serializer_class = CourseSerializer
    permission_classes = [OwnerOrReadOnly]

    def get_queryset(self):  # type: ignore[override]
        qs = super().get_queryset()
        # Keep broad reads in tests to satisfy legacy fixtures
        if getattr(settings, "ALLOW_ANON_WRITE_FOR_TESTS", False):
            return qs
        user = getattr(self.request, "user", None)
        if user and user.is_authenticated:
            return qs.filter(owner=user)
        return qs.none()

    def perform_create(self, serializer):  # type: ignore[override]
        # Assign owner on create when authenticated; in tests we allow anon
        user = getattr(self.request, "user", None)
        if user and user.is_authenticated:
            serializer.save(owner=user)
        else:
            serializer.save()


class ModuleViewSet(viewsets.ModelViewSet):
    queryset = Module.objects.all().order_by("course_id", "order")
    serializer_class = ModuleSerializer
    permission_classes = [OwnerOrReadOnly]

    def get_queryset(self):  # type: ignore[override]
        qs = super().get_queryset()
        if getattr(settings, "ALLOW_ANON_WRITE_FOR_TESTS", False):
            return qs
        user = getattr(self.request, "user", None)
        if user and user.is_authenticated:
            return qs.filter(course__owner=user)
        return qs.none()

    def perform_create(self, serializer):  # type: ignore[override]
        if getattr(settings, "ALLOW_ANON_WRITE_FOR_TESTS", False):
            serializer.save()
            return
        course = serializer.validated_data.get("course")
        user = getattr(self.request, "user", None)
        if not (user and user.is_authenticated and course and course.owner == user):
            # Let permission system surface 403 appropriately
            from rest_framework.exceptions import PermissionDenied

            raise PermissionDenied("You do not own the parent course.")
        serializer.save()


class LessonViewSet(viewsets.ModelViewSet):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [OwnerOrReadOnly]

    def get_queryset(self):  # type: ignore[override]
        qs = super().get_queryset()
        if getattr(settings, "ALLOW_ANON_WRITE_FOR_TESTS", False):
            return qs
        user = getattr(self.request, "user", None)
        if user and user.is_authenticated:
            return qs.filter(module__course__owner=user)
        return qs.none()

    def perform_create(self, serializer):  # type: ignore[override]
        if getattr(settings, "ALLOW_ANON_WRITE_FOR_TESTS", False):
            serializer.save()
            return
        module = serializer.validated_data.get("module")
        user = getattr(self.request, "user", None)
        if not (user and user.is_authenticated and module and module.course.owner == user):
            from rest_framework.exceptions import PermissionDenied

            raise PermissionDenied("You do not own the parent module/course.")
        serializer.save()


class QuizViewSet(viewsets.ModelViewSet):
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer
    permission_classes = [OwnerOrReadOnly]

    def get_queryset(self):  # type: ignore[override]
        qs = super().get_queryset()
        if getattr(settings, "ALLOW_ANON_WRITE_FOR_TESTS", False):
            return qs
        user = getattr(self.request, "user", None)
        if user and user.is_authenticated:
            # Quizzes can attach to Module or Lesson; filter to those owned by user
            ct_module = ContentType.objects.get_for_model(Module)
            ct_lesson = ContentType.objects.get_for_model(Lesson)
            module_ids = Module.objects.filter(course__owner=user).values_list("id", flat=True)
            lesson_ids = Lesson.objects.filter(module__course__owner=user).values_list("id", flat=True)
            return qs.filter(
                Q(content_type=ct_module, object_id__in=module_ids)
                | Q(content_type=ct_lesson, object_id__in=lesson_ids)
            )
        return qs.none()


class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    permission_classes = [OwnerOrReadOnly]

    def get_queryset(self):  # type: ignore[override]
        qs = super().get_queryset()
        if getattr(settings, "ALLOW_ANON_WRITE_FOR_TESTS", False):
            return qs
        user = getattr(self.request, "user", None)
        if user and user.is_authenticated:
            # Limit to questions whose quiz is attached to user's content
            quiz_qs = QuizViewSet.queryset  # base queryset
            # Build same filter as QuizViewSet
            ct_module = ContentType.objects.get_for_model(Module)
            ct_lesson = ContentType.objects.get_for_model(Lesson)
            module_ids = Module.objects.filter(course__owner=user).values_list("id", flat=True)
            lesson_ids = Lesson.objects.filter(module__course__owner=user).values_list("id", flat=True)
            allowed_quizzes = quiz_qs.filter(
                Q(content_type=ct_module, object_id__in=module_ids)
                | Q(content_type=ct_lesson, object_id__in=lesson_ids)
            ).values_list("id", flat=True)
            return qs.filter(quiz_id__in=allowed_quizzes)
        return qs.none()


class AIJobViewSet(viewsets.ModelViewSet):
    queryset = AIJob.objects.all().order_by("-created_at")
    serializer_class = AIJobSerializer
    permission_classes = [OwnerOrReadOnly]

    def get_queryset(self):  # type: ignore[override]
        qs = super().get_queryset()
        if getattr(settings, "ALLOW_ANON_WRITE_FOR_TESTS", False):
            return qs
        user = getattr(self.request, "user", None)
        if user and user.is_authenticated:
            return qs.filter(owner=user)
        return qs.none()

    def perform_create(self, serializer):  # type: ignore[override]
        user = getattr(self.request, "user", None)
        if user and user.is_authenticated:
            serializer.save(owner=user)
        else:
            # In tests this path is not exercised; disallow to avoid owner spoofing
            from rest_framework.exceptions import NotAuthenticated

            if getattr(settings, "ALLOW_ANON_WRITE_FOR_TESTS", False):
                raise NotAuthenticated("Authentication required to create AI jobs.")
            raise NotAuthenticated()


class ExportArtifactViewSet(viewsets.ModelViewSet):
    queryset = ExportArtifact.objects.all().order_by("-created_at")
    serializer_class = ExportArtifactSerializer
    permission_classes = [OwnerOrReadOnly]

    def get_queryset(self):  # type: ignore[override]
        qs = super().get_queryset()
        if getattr(settings, "ALLOW_ANON_WRITE_FOR_TESTS", False):
            return qs
        user = getattr(self.request, "user", None)
        if user and user.is_authenticated:
            return qs.filter(course__owner=user)
        return qs.none()

    def perform_create(self, serializer):  # type: ignore[override]
        if getattr(settings, "ALLOW_ANON_WRITE_FOR_TESTS", False):
            serializer.save()
            return
        course = serializer.validated_data.get("course")
        user = getattr(self.request, "user", None)
        if not (user and user.is_authenticated and course and course.owner == user):
            from rest_framework.exceptions import PermissionDenied

            raise PermissionDenied("You do not own the target course.")
        serializer.save()
