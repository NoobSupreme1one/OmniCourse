"""
API URL configuration.
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import (
    AIJobViewSet,
    CourseViewSet,
    ExportArtifactViewSet,
    LessonViewSet,
    ModuleViewSet,
    QuestionViewSet,
    QuizViewSet,
    healthz,
    livez,
    readinessz,
)

# Create router and register viewsets
router = DefaultRouter()
router.register(r"courses", CourseViewSet)
router.register(r"modules", ModuleViewSet)
router.register(r"lessons", LessonViewSet)
router.register(r"quizzes", QuizViewSet)
router.register(r"questions", QuestionViewSet)
router.register(r"jobs", AIJobViewSet)
router.register(r"artifacts", ExportArtifactViewSet)

urlpatterns = [
    path("healthz", healthz, name="healthz"),
    path("livez", livez, name="livez"),
    path("readinessz", readinessz, name="readinessz"),
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("", include(router.urls)),
]
