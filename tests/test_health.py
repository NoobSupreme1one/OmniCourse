import json
from django.test import Client


def test_health_endpoints_smoke(db):
    c = Client()
    for path in ("/api/v1/healthz", "/api/v1/livez", "/api/v1/readinessz"):
        resp = c.get(path)
        assert resp.status_code == 200
        body = json.loads(resp.content)
        assert "ok" in body
