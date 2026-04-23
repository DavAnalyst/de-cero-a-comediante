import json
import pytest
from app.extensions import db
from app.models import Course, Purchase


def _register_and_token(client, email="student@test.com"):
    rv = client.post(
        "/api/auth/register",
        data=json.dumps({"email": email, "name": "Student", "password": "password123"}),
        content_type="application/json",
    )
    return rv.get_json()["token"], rv.get_json()["user"]["id"]


def _create_course(app, published=True):
    with app.app_context():
        course = Course(title="Stand-up 101", price_cop=199000, is_published=published)
        db.session.add(course)
        db.session.commit()
        return course.id


def test_list_courses_public(client, app):
    _create_course(app)
    rv = client.get("/api/courses")
    assert rv.status_code == 200
    assert len(rv.get_json()) == 1


def test_list_courses_only_published(client, app):
    _create_course(app, published=False)
    rv = client.get("/api/courses")
    assert rv.status_code == 200
    assert rv.get_json() == []


def test_course_detail_public(client, app):
    course_id = _create_course(app)
    rv = client.get(f"/api/courses/{course_id}")
    assert rv.status_code == 200
    assert rv.get_json()["id"] == course_id


def test_course_lessons_no_auth(client, app):
    course_id = _create_course(app)
    rv = client.get(f"/api/courses/{course_id}/lessons")
    assert rv.status_code == 401


def test_course_lessons_not_enrolled(client, app):
    course_id = _create_course(app)
    token, _ = _register_and_token(client)
    rv = client.get(
        f"/api/courses/{course_id}/lessons",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert rv.status_code == 403
