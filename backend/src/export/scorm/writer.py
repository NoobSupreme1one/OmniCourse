"""
Minimal SCORM 1.2 writer for MVP.

Generates a simple package with:
- imsmanifest.xml
- api.js (stub runtime)
- lesson HTML pages under lessons/
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Dict, List, Tuple

from ..common.zipper import build_deterministic_zip


@dataclass
class LessonData:
    id: str
    title: str
    html: str


@dataclass
class CourseData:
    id: str
    title: str
    lessons: list[LessonData]


def _slugify(value: str) -> str:
    allowed = "abcdefghijklmnopqrstuvwxyz0123456789-"
    out = []
    last_dash = False
    for ch in value.lower():
        if ch.isalnum():
            out.append(ch)
            last_dash = False
        else:
            if not last_dash:
                out.append("-")
                last_dash = True
    result = "".join(out).strip("-")
    return result or "course"


def _imsmanifest_xml(course: CourseData) -> bytes:
    org_id = f"org-{_slugify(course.title)}"
    res_items = []
    resources = []
    for idx, lesson in enumerate(course.lessons, start=1):
        item_id = f"item-{idx}"
        res_id = f"res-{idx}"
        href = f"lessons/{lesson.id}.html"
        res_items.append(
            f'<item identifier="{item_id}" identifierref="{res_id}"><title>{_xml(lesson.title)}</title></item>'
        )
        resources.append(
            f'<resource identifier="{res_id}" type="webcontent" href="{href}"><file href="{href}"/></resource>'
        )

    xml = f"""
<?xml version="1.0" encoding="UTF-8"?>
<manifest identifier="man-{_slugify(course.title)}" version="1.2"
    xmlns="http://www.imsproject.org/xsd/imscp_rootv1p1p2"
    xmlns:adlcp="http://www.adlnet.org/xsd/adlcp_rootv1p2"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xsi:schemaLocation="http://www.imsproject.org/xsd/imscp_rootv1p1p2 imscp_rootv1p1p2.xsd
    http://www.adlnet.org/xsd/adlcp_rootv1p2 adlcp_rootv1p2.xsd">
  <organizations default="{org_id}">
    <organization identifier="{org_id}">
      <title>{_xml(course.title)}</title>
      {''.join(res_items)}
    </organization>
  </organizations>
  <resources>
    {''.join(resources)}
  </resources>
</manifest>
""".strip()
    return xml.encode("utf-8")


def _xml(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&apos;")
    )


def _lesson_html(title: str, body_html: str) -> bytes:
    # Minimal runtime shim to set lesson_status on window load
    html = f"""
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <title>{_xml(title)}</title>
    <script src="../api.js"></script>
  </head>
  <body>
    <h1>{_xml(title)}</h1>
    <div class="content">{body_html}</div>
    <script>if (window.SCORM_API) {{ try {{ SCORM_API.setStatus('completed'); }} catch (e) {{}} }}</script>
  </body>
</html>
""".strip()
    return html.encode("utf-8")


def _api_js() -> bytes:
    return (
        """
// Minimal SCORM 1.2 runtime shim (MVP)
window.SCORM_API = {
  setStatus: function (status) { try { console.log('SCORM status:', status); } catch (e) {} }
};
""".strip().encode("utf-8")
    )


def build_scorm_files(course: CourseData) -> dict[str, bytes]:
    files: Dict[str, bytes] = {}
    # Manifest
    files["imsmanifest.xml"] = _imsmanifest_xml(course)
    # Runtime
    files["api.js"] = _api_js()
    # Lessons
    for lesson in course.lessons:
        files[f"lessons/{lesson.id}.html"] = _lesson_html(lesson.title, lesson.html)
    return files


def build_scorm_zip(course: CourseData) -> Tuple[bytes, Dict[str, str]]:
    """
    Build a SCORM ZIP and return (zip_bytes, checksums_by_path).
    """
    files = build_scorm_files(course)
    checksums = {p: hashlib.sha256(b).hexdigest() for p, b in files.items()}
    return build_deterministic_zip(files), checksums
