"""
Job models for OmniCourse project.
"""

import uuid

from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models


class AIJob(models.Model):
    """
    Async job for AI content generation tasks.
    """

    class JobKind(models.TextChoices):
        OUTLINE = "outline", "Course Outline"
        LESSON = "lesson", "Lesson Generation"
        QUIZ = "quiz", "Quiz Generation"
        LECTURE = "lecture", "Lecture Materials"
        EXPORT = "export", "Content Export"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        RUNNING = "running", "Running"
        COMPLETED = "completed", "Completed"
        FAILED = "failed", "Failed"
        CANCELLED = "cancelled", "Cancelled"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Job metadata
    kind = models.CharField(max_length=20, choices=JobKind.choices)
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.PENDING
    )

    # User and ownership
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="ai_jobs")

    # Input reference (generic foreign key to any model)
    input_content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        related_name="ai_jobs_as_input",
        null=True,
        blank=True,
    )
    input_object_id = models.CharField(max_length=36, null=True, blank=True)
    input_object = GenericForeignKey("input_content_type", "input_object_id")

    # Input data (JSON for flexible parameters)
    input_data = models.JSONField(
        default=dict, help_text="Input parameters for the job"
    )

    # Output reference (generic foreign key to created content)
    output_content_type = models.ForeignKey(
        ContentType,
        on_delete=models.SET_NULL,
        related_name="ai_jobs_as_output",
        null=True,
        blank=True,
    )
    output_object_id = models.CharField(max_length=36, null=True, blank=True)
    output_object = GenericForeignKey("output_content_type", "output_object_id")

    # Output data (for results that don't map to models)
    output_data = models.JSONField(default=dict, help_text="Output data from the job")

    # Job execution details
    celery_task_id = models.CharField(max_length=36, null=True, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    # Error tracking
    error_message = models.TextField(blank=True)
    retry_count = models.PositiveIntegerField(default=0)

    # Cost tracking
    cost_cents = models.PositiveIntegerField(
        default=0, help_text="Cost in cents for this job"
    )
    token_usage = models.JSONField(default=dict, help_text="Token usage breakdown")

    # Progress tracking
    progress_percentage = models.PositiveIntegerField(default=0)
    progress_message = models.CharField(max_length=255, blank=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["owner", "status"]),
            models.Index(fields=["kind", "status"]),
            models.Index(fields=["celery_task_id"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return f"{self.kind} job {self.id} ({self.status})"

    @property
    def duration_seconds(self):
        """Get job duration in seconds."""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None

    @property
    def is_finished(self):
        """Check if job is in a terminal state."""
        return self.status in [
            self.Status.COMPLETED,
            self.Status.FAILED,
            self.Status.CANCELLED,
        ]


class ExportArtifact(models.Model):
    """
    Generated export artifacts (files) for courses.
    """

    class ExportKind(models.TextChoices):
        OLX = "olx", "Open edX (OLX)"
        SCORM = "scorm", "SCORM 1.2"
        QTI = "qti", "QTI 2.1"
        UDEMY = "udemy", "Udemy Bundle"
        TEACHABLE = "teachable", "Teachable Bundle"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Content reference
    course = models.ForeignKey(
        "courses.Course", on_delete=models.CASCADE, related_name="export_artifacts"
    )

    # Export details
    kind = models.CharField(max_length=20, choices=ExportKind.choices)
    file_path = models.CharField(max_length=500, help_text="S3 path to the export file")
    file_size_bytes = models.PositiveBigIntegerField(default=0)
    checksum = models.CharField(max_length=64, help_text="SHA256 checksum")

    # Export metadata
    export_settings = models.JSONField(
        default=dict, help_text="Settings used for this export"
    )

    # Job reference
    job = models.ForeignKey(
        AIJob,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="artifacts",
    )

    # Access and downloads
    download_count = models.PositiveIntegerField(default=0)
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When this artifact expires and should be deleted",
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["course", "kind"]),
            models.Index(fields=["created_at"]),
            models.Index(fields=["expires_at"]),
        ]

    def __str__(self):
        return f"{self.course.title} - {self.kind} export"

    @property
    def file_size_mb(self):
        """Get file size in MB."""
        return round(self.file_size_bytes / (1024 * 1024), 2)


class IdempotencyKey(models.Model):
    """
    Store idempotency keys to prevent duplicate job creation.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    key = models.CharField(max_length=255, unique=True)
    request_hash = models.CharField(max_length=64)

    # Response data
    response_data = models.JSONField()
    response_status = models.PositiveIntegerField()

    # Reference to created job
    job = models.ForeignKey(
        AIJob,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="idempotency_keys",
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(help_text="When this key expires")

    class Meta:
        indexes = [
            models.Index(fields=["key"]),
            models.Index(fields=["expires_at"]),
        ]

    def __str__(self):
        return f"Idempotency key {self.key}"
