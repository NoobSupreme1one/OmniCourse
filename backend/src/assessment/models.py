"""
Assessment models for OmniCourse project.
"""

import uuid

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Quiz(models.Model):
    """
    Quiz/assessment entity that can be attached to lessons or modules.
    """

    class Difficulty(models.TextChoices):
        EASY = "easy", "Easy"
        MEDIUM = "medium", "Medium"
        HARD = "hard", "Hard"

    class ExportFormat(models.TextChoices):
        QTI = "qti", "QTI 2.1"
        SCORM = "scorm", "SCORM 1.2"
        GIFT = "gift", "GIFT"
        JSON = "json", "JSON"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    # Generic foreign key to attach to lesson or module
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.CharField(max_length=36)  # UUID field
    content_object = GenericForeignKey("content_type", "object_id")

    # Quiz settings
    difficulty = models.CharField(
        max_length=10, choices=Difficulty.choices, default=Difficulty.MEDIUM
    )
    target_questions = models.PositiveIntegerField(
        default=5, validators=[MinValueValidator(1), MaxValueValidator(50)]
    )
    time_limit_minutes = models.PositiveIntegerField(
        null=True, blank=True, validators=[MinValueValidator(1), MaxValueValidator(300)]
    )

    # Export settings
    export_formats = models.JSONField(
        default=list, help_text="List of export formats for this quiz"
    )

    # Learning objectives mapping
    learning_objectives = models.JSONField(
        default=list, help_text="Learning objectives this quiz assesses"
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["content_type", "object_id"]),
        ]

    def __str__(self):
        return self.title

    @property
    def question_count(self):
        """Get actual number of questions."""
        return self.questions.count()


class Question(models.Model):
    """
    Individual question within a quiz.
    """

    class QuestionType(models.TextChoices):
        MCQ = "mcq", "Multiple Choice (Single)"
        MSQ = "msq", "Multiple Choice (Multiple)"
        TRUE_FALSE = "true_false", "True/False"
        SHORT_ANSWER = "short_answer", "Short Answer"
        ESSAY = "essay", "Essay"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="questions")

    # Question content
    question_type = models.CharField(max_length=20, choices=QuestionType.choices)
    prompt = models.TextField(help_text="The question text")
    order = models.PositiveIntegerField(default=0)

    # Scoring
    points = models.PositiveIntegerField(
        default=1, validators=[MinValueValidator(1), MaxValueValidator(100)]
    )

    # Answer data (stored as JSON for flexibility)
    choices = models.JSONField(
        default=list, help_text="Answer choices for MCQ/MSQ questions"
    )
    correct_answer = models.JSONField(
        help_text="Correct answer(s) - format depends on question type"
    )
    rationale = models.TextField(
        blank=True, help_text="Explanation for the correct answer"
    )

    # Learning objective mapping
    learning_objective = models.CharField(
        max_length=255,
        blank=True,
        help_text="Learning objective this question assesses",
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["order", "created_at"]
        unique_together = ["quiz", "order"]
        indexes = [
            models.Index(fields=["quiz", "order"]),
            models.Index(fields=["question_type"]),
        ]

    def __str__(self):
        return f"{self.quiz.title} - Q{self.order + 1}"

    def clean(self):
        """Validate question data based on type."""
        from django.core.exceptions import ValidationError

        if self.question_type in ["mcq", "msq"] and not self.choices:
            raise ValidationError("MCQ/MSQ questions must have choices")

        if self.question_type == "true_false" and self.correct_answer not in [
            True,
            False,
        ]:
            raise ValidationError("True/False questions must have boolean answer")


class LearningObjective(models.Model):
    """
    Learning objectives that can be mapped to questions and lessons.
    """

    class BloomLevel(models.TextChoices):
        REMEMBER = "remember", "Remember"
        UNDERSTAND = "understand", "Understand"
        APPLY = "apply", "Apply"
        ANALYZE = "analyze", "Analyze"
        EVALUATE = "evaluate", "Evaluate"
        CREATE = "create", "Create"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Content
    text = models.TextField(help_text="The learning objective statement")
    bloom_level = models.CharField(
        max_length=20, choices=BloomLevel.choices, default=BloomLevel.UNDERSTAND
    )

    # Generic foreign key to attach to course, module, or lesson
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.CharField(max_length=36)  # UUID field
    content_object = GenericForeignKey("content_type", "object_id")

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["created_at"]
        indexes = [
            models.Index(fields=["content_type", "object_id"]),
            models.Index(fields=["bloom_level"]),
        ]

    def __str__(self):
        return self.text[:100] + "..." if len(self.text) > 100 else self.text
