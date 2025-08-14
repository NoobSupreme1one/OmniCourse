"""
SCORM export service wiring ORM -> writer.

Takes a Course, renders lesson HTML, builds a deterministic SCORM zip,
writes it to MEDIA_ROOT, and records an ExportArtifact with checksums.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

from django.conf import settings
from django.contrib.auth.models import User

from courses.models import Course, Lesson, Module
from jobs.models import ExportArtifact
from .writer import CourseData, LessonData, build_scorm_zip


def _lesson_html_from_model(lesson: Lesson) -> str:
    # Use simple preformatted body to avoid markdown deps
    import html as _html

    content = getattr(lesson, "content", None) or getattr(lesson, "markdown", "")
    safe = _html.escape(content)
    return f"<pre>{safe}</pre>"


def export_course_to_scorm(course: Course, *, owner: User | None = None) -> ExportArtifact:
    # Collect lessons ordered by module.order then lesson.order
    modules = (
        Module.objects.filter(course=course).order_by("order", "created_at").all()
    )
    lessons = []
    for m in modules:
        for lesson in m.lessons.all().order_by("order", "created_at"):
            lessons.append(
                LessonData(
                    id=str(lesson.id),
                    title=lesson.title,
                    html=_lesson_html_from_model(lesson),
                )
            )

    course_data = CourseData(id=str(course.id), title=course.title, lessons=lessons)
    zip_bytes, checksums = build_scorm_zip(course_data)

    # Compute overall archive checksum
    archive_sha = hashlib.sha256(zip_bytes).hexdigest()
    size_bytes = len(zip_bytes)

    # Write to MEDIA_ROOT/exports/scorm/<course_id>/package.zip
    media_root = Path(getattr(settings, "MEDIA_ROOT", "."))
    out_dir = media_root / "exports" / "scorm" / str(course.id)
    out_dir.mkdir(parents=True, exist_ok=True)
    filename = f"{_slug(course.title)}.zip"
    out_path = out_dir / filename
    out_path.write_bytes(zip_bytes)

    # Persist artifact
    artifact = ExportArtifact.objects.create(
        course=course,
        kind=ExportArtifact.ExportKind.SCORM,
        file_path=str(out_path),
        file_size_bytes=size_bytes,
        checksum=archive_sha,
        export_settings={
            "lesson_count": len(lessons),
            "file_checksums": checksums,
        },
        job=None,
    )
    return artifact


def _slug(text: str) -> str:
    import re

    s = text.lower()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s or "course"
