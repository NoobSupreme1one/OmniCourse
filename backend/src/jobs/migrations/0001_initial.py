from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="AIJob",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("kind", models.CharField(choices=[("OUTLINE", "Outline"), ("LESSON", "Lesson"), ("QUIZ", "Quiz"), ("LECTURE", "Lecture"), ("EXPORT", "Export")], max_length=16)),
                ("input_ref", models.CharField(max_length=255)),
                ("status", models.CharField(default="PENDING", max_length=16)),
                ("cost_cents", models.IntegerField(default=0)),
                ("output_ref", models.CharField(blank=True, max_length=255)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name="ExportArtifact",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("course_id", models.IntegerField()),
                ("kind", models.CharField(max_length=16)),
                ("path_s3", models.CharField(max_length=512)),
                ("checksum", models.CharField(max_length=64)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]

