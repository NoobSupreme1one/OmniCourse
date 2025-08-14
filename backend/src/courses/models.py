"""
Course models for OmniCourse project.
"""

import uuid

from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Course(models.Model):
    """
    Main course entity containing modules, lessons, and assessments.
    """

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        ACTIVE = "active", "Active"
        ARCHIVED = "archived", "Archived"

    class PlatformTarget(models.TextChoices):
        OPEN_EDX = "open_edx", "Open edX"
        SCORM = "scorm", "SCORM 1.2"
        QTI = "qti", "QTI 2.1"
        UDEMY = "udemy", "Udemy"
        TEACHABLE = "teachable", "Teachable"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    audience = models.CharField(max_length=255, help_text="Target audience description")
    goals = models.JSONField(default=list, help_text="Learning goals/outcomes")
    platform_targets = models.JSONField(
        default=list, help_text="Target export platforms"
    )
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.DRAFT
    )

    # Metadata
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="courses",
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Course settings
    estimated_hours = models.PositiveIntegerField(
        default=0, validators=[MinValueValidator(0), MaxValueValidator(1000)]
    )

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["owner", "status"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return self.title


class Module(models.Model):
    """
    Course module containing related lessons.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="modules")
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["order", "created_at"]
        unique_together = ["course", "order"]
        indexes = [
            models.Index(fields=["course", "order"]),
        ]

    def __str__(self):
        return f"{self.course.title} - {self.title}"


class Lesson(models.Model):
    """
    Individual lesson with content and learning objectives.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name="lessons")
    title = models.CharField(max_length=255)
    content = models.TextField(help_text="Lesson content in Markdown format")
    learning_objectives = models.JSONField(
        default=list, help_text="List of learning objectives"
    )

    # Content metadata
    estimated_minutes = models.PositiveIntegerField(
        default=10, validators=[MinValueValidator(1), MaxValueValidator(180)]
    )
    order = models.PositiveIntegerField(default=0)

    # Assets and resources
    assets = models.JSONField(
        default=list, help_text="List of asset references (images, videos, files)"
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["order", "created_at"]
        unique_together = ["module", "order"]
        indexes = [
            models.Index(fields=["module", "order"]),
        ]

    def __str__(self):
        return f"{self.module.title} - {self.title}"

    @property
    def course(self):
        """Get the parent course."""
        return self.module.course
