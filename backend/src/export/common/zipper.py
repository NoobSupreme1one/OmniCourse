"""
Deterministic ZIP utilities.

Creates archives with stable file ordering, normalized permissions, and fixed timestamps
so that byte-for-byte archives are reproducible in tests and CI.
"""

from __future__ import annotations

import io
import zipfile


FIXED_TIME = (1980, 1, 1, 0, 0, 0)  # MS-DOS epoch used by zip files


def build_deterministic_zip(files: dict[str, bytes]) -> bytes:
    """
    Build a deterministic ZIP from a mapping of path -> bytes.

    - Paths are sorted lexicographically
    - All ZipInfo date_time set to FIXED_TIME
    - External attributes set to 0o644 for files
    """
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(files.keys()):
            data = files[path]
            info = zipfile.ZipInfo(filename=path, date_time=FIXED_TIME)
            info.external_attr = (0o644 & 0xFFFF) << 16  # -rw-r--r--
            # Ensure consistent metadata
            info.create_system = 3  # Unix
            info.compress_type = zipfile.ZIP_DEFLATED
            zf.writestr(info, data)

    return buf.getvalue()
