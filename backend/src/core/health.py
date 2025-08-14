"""
Health check utilities for OmniCourse.

Provides lightweight checks for database, broker, and storage backends
that degrade gracefully when optional dependencies are unavailable.
"""

from __future__ import annotations

import socket
from dataclasses import dataclass
from typing import Any

from django.conf import settings
from django.db import connections


@dataclass
class CheckResult:
    ok: bool
    detail: str | None = None
    extra: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        data = {"ok": self.ok}
        if self.detail:
            data["detail"] = self.detail
        if self.extra:
            data.update(self.extra)
        return data


def check_database() -> CheckResult:
    try:
        with connections["default"].cursor() as cursor:
            cursor.execute("SELECT version()")
            row = cursor.fetchone()
            version = row[0] if row else "unknown"
        return CheckResult(ok=True, extra={"engine": connections["default"].settings_dict.get("ENGINE", "unknown"), "version": version})
    except Exception as exc:  # noqa: BLE001
        return CheckResult(ok=False, detail=str(exc))


def _parse_redis_url(url: str) -> tuple[str, int, int]:
    # Very small parser for redis URLs like redis://host:port/db
    # Defaults to localhost:6379/0 if missing parts
    default_host, default_port, default_db = "localhost", 6379, 0
    try:
        if not url.startswith("redis://"):
            return default_host, default_port, default_db
        without_scheme = url[len("redis://") :]
        host_port, _, db_str = without_scheme.partition("/")
        host, _, port_str = host_port.partition(":")
        host = host or default_host
        port = int(port_str) if port_str else default_port
        db = int(db_str) if db_str else default_db
        return host, port, db
    except Exception:
        return default_host, default_port, default_db


def check_broker() -> CheckResult:
    broker_url = getattr(settings, "CELERY_BROKER_URL", "")
    if not broker_url:
        return CheckResult(ok=False, detail="No broker configured", extra={"type": "unknown"})

    # Prefer using redis library if available, otherwise do a simple TCP check
    if broker_url.startswith("redis://"):
        host, port, db = _parse_redis_url(broker_url)
        try:
            try:
                import redis  # type: ignore

                client = redis.Redis(host=host, port=port, db=db, socket_connect_timeout=0.5, socket_timeout=0.5)
                pong = client.ping()
                return CheckResult(ok=bool(pong), extra={"type": "redis", "host": host, "port": port, "db": db})
            except Exception:
                # Fallback to raw socket if redis not usable
                with socket.create_connection((host, port), timeout=0.5) as s:
                    s.sendall(b"PING\r\n")
                    _ = s.recv(16)
                return CheckResult(ok=True, extra={"type": "redis", "host": host, "port": port, "db": db})
        except Exception as exc:  # noqa: BLE001
            return CheckResult(ok=False, detail=str(exc), extra={"type": "redis", "host": host, "port": port, "db": db})

    # Unknown broker type; just report configured
    return CheckResult(ok=True, detail="Broker configured", extra={"type": "unknown", "url": broker_url})


def check_storage() -> CheckResult:
    bucket = getattr(settings, "AWS_STORAGE_BUCKET_NAME", "")
    region = getattr(settings, "AWS_S3_REGION_NAME", "")

    if not bucket:
        return CheckResult(ok=False, detail="No bucket configured")

    # If boto3 is available, attempt a lightweight head-bucket
    try:
        import boto3  # type: ignore
        from botocore.exceptions import ClientError  # type: ignore

        s3 = boto3.client("s3", region_name=region or None)
        try:
            s3.head_bucket(Bucket=bucket)
            return CheckResult(ok=True, extra={"bucket": bucket, "region": region or "auto"})
        except ClientError as exc:  # type: ignore
            return CheckResult(ok=False, detail=str(exc), extra={"bucket": bucket, "region": region or "auto"})
    except Exception:
        # Degrade gracefully if boto3 not present; report configuration only
        return CheckResult(ok=True, detail="SDK not available; configuration only", extra={"bucket": bucket, "region": region or "auto"})


def health_payload() -> dict[str, Any]:
    db = check_database().to_dict()
    broker = check_broker().to_dict()
    storage = check_storage().to_dict()

    return {
        "ok": bool(db.get("ok") and broker.get("ok") and storage.get("ok")),
        "app": {
            "debug": bool(getattr(settings, "DEBUG", False)),
            "environment": getattr(settings, "ENVIRONMENT", "dev"),
        },
        "dependencies": {"db": db, "broker": broker, "storage": storage},
    }
