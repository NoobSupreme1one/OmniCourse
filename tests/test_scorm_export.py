import hashlib
from export.scorm.writer import CourseData, LessonData, build_scorm_zip


def test_scorm_zip_matches_golden(tmp_path):
    # Prepare a deterministic course with two lessons
    course = CourseData(
        id="course-1",
        title="MVP Sample Course",
        lessons=[
            LessonData(id="lesson-1", title="Introduction", html="<p>Hello world.</p>"),
            LessonData(id="lesson-2", title="Basics", html="<p>Getting started.</p>"),
        ],
    )

    zip_bytes, checksums = build_scorm_zip(course)

    # Write zip to disk to debug when needed
    (tmp_path / "out.zip").write_bytes(zip_bytes)

    # Build manifest lines: sha256  size  path
    import zipfile

    with zipfile.ZipFile(tmp_path / "out.zip", "r") as zf:
        paths = sorted(zf.namelist())
        manifest_lines = []
        for p in paths:
            data = zf.read(p)
            sha = hashlib.sha256(data).hexdigest()
            size = len(data)
            manifest_lines.append(f"{sha}  {size:8d}  {p}")

    generated = "\n".join(manifest_lines).strip() + "\n"

    golden_path = "tests/golden/scorm/MANIFEST.txt"
    with open(golden_path, "r", encoding="utf-8") as f:
        golden = f.read()

    assert generated == golden
