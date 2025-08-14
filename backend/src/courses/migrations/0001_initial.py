import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Course",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=255)),
                ("audience", models.CharField(blank=True, max_length=255)),
                ("goals", models.JSONField(blank=True, default=list)),
                ("platform_targets", models.JSONField(blank=True, default=list)),
                ("status", models.CharField(default="draft", max_length=32)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name="Module",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=255)),
                ("order", models.PositiveIntegerField(default=0)),
                (
                    "course",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="modules", to="courses.course"),
                ),
            ],
            options={"ordering": ["order", "id"]},
        ),
        migrations.CreateModel(
            name="Lesson",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=255)),
                ("markdown", models.TextField(blank=True)),
                ("est_minutes", models.PositiveIntegerField(default=10)),
                ("assets", models.JSONField(blank=True, default=list)),
                (
                    "module",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="lessons", to="courses.module"),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Quiz",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("owner_ref", models.CharField(help_text="lesson:{id} or module:{id}", max_length=64)),
                ("policy", models.JSONField(blank=True, default=dict)),
                ("export_formats", models.JSONField(blank=True, default=list)),
            ],
        ),
        migrations.CreateModel(
            name="Question",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("type", models.CharField(default="mcq", max_length=8)),
                ("prompt", models.TextField()),
                ("choices", models.JSONField(blank=True, default=list)),
                ("answer_key", models.JSONField(blank=True, default=dict)),
                ("rationale", models.TextField(blank=True)),
                (
                    "quiz",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="questions", to="courses.quiz"),
                ),
            ],
        ),
    ]

