from __future__ import annotations

from django.core.management.base import BaseCommand, CommandError

from courses.models import Course
from export.scorm.service import export_course_to_scorm


class Command(BaseCommand):
    help = "Export a Course to a SCORM 1.2 package and persist an ExportArtifact"

    def add_arguments(self, parser):
        parser.add_argument("course_id", type=str, help="UUID of the Course to export")

    def handle(self, *args, **options):  # noqa: ARG002
        course_id = options["course_id"]
        try:
            course = Course.objects.get(id=course_id)
        except Course.DoesNotExist as e:  # noqa: F841
            raise CommandError(f"Course not found: {course_id}")

        artifact = export_course_to_scorm(course)
        self.stdout.write(
            self.style.SUCCESS(
                f"Exported SCORM: path={artifact.file_path} size={artifact.file_size_bytes} checksum={artifact.checksum}"
            )
        )

