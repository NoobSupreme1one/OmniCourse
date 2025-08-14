from rest_framework import serializers

from assessment.models import Question, Quiz
from courses.models import Course, Lesson, Module
from jobs.models import AIJob, ExportArtifact


class ModuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Module
        fields = ["id", "course", "title", "order"]


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = [
            "id",
            "module",
            "title",
            "content",
            "estimated_minutes",
            "assets",
            "learning_objectives",
            "order",
        ]


class CourseSerializer(serializers.ModelSerializer):
    modules = ModuleSerializer(many=True, read_only=True)

    class Meta:
        model = Course
        fields = [
            "id",
            "title",
            "audience",
            "goals",
            "platform_targets",
            "status",
            "created_at",
            "updated_at",
            "modules",
        ]


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = [
            "id",
            "quiz",
            "question_type",
            "prompt",
            "choices",
            "correct_answer",
            "rationale",
            "order",
            "points",
            "learning_objective",
        ]


class QuizSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Quiz
        fields = [
            "id",
            "title",
            "description",
            "difficulty",
            "target_questions",
            "time_limit_minutes",
            "export_formats",
            "learning_objectives",
            "questions",
            "created_at",
            "updated_at",
        ]


class AIJobSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIJob
        fields = [
            "id",
            "kind",
            "status",
            "owner",
            "input_data",
            "output_data",
            "celery_task_id",
            "started_at",
            "completed_at",
            "error_message",
            "retry_count",
            "cost_cents",
            "token_usage",
            "progress_percentage",
            "progress_message",
            "created_at",
            "updated_at",
        ]


class ExportArtifactSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExportArtifact
        fields = [
            "id",
            "course",
            "kind",
            "file_path",
            "file_size_bytes",
            "checksum",
            "export_settings",
            "job",
            "download_count",
            "expires_at",
            "created_at",
            "updated_at",
        ]
