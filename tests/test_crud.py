import json
from django.test import Client
from .factories import CourseFactory


def test_create_and_list_courses(db):
    client = Client()
    # Create
    payload = {"title": "Test Course", "audience": "students"}
    resp = client.post("/api/v1/courses/", data=json.dumps(payload), content_type="application/json")
    assert resp.status_code in (200, 201)
    # List
    resp = client.get("/api/v1/courses/")
    assert resp.status_code == 200
    data = resp.json()
    # DRF may return a list or paginated; handle both
    items = data if isinstance(data, list) else data.get("results", [])
    assert any(item.get("title") == "Test Course" for item in items)


def test_nested_modules_visible(db):
    c = CourseFactory()
    client = Client()
    resp = client.get(f"/api/v1/courses/{c.id}/")
    assert resp.status_code == 200
    assert "modules" in resp.json()
