import json
from app.extensions import db
from app.models import Course, Lesson, Purchase


def _setup(client, app):
    rv = client.post(
        "/api/auth/register",
        data=json.dumps({"email": "p@test.com", "name": "Prog", "password": "password123"}),
        content_type="application/json",
    )
    body = rv.get_json()
    token = body["token"]
    user_id = body["user"]["id"]

    with app.app_context():
        course = Course(title="Course", price_cop=100000, is_published=True)
        db.session.add(course)
        db.session.flush()
        lesson = Lesson(
            course_id=course.id,
            module_num=1,
            module_name="Mod 1",
            order_in_module=1,
            title="Lesson 1",
        )
        db.session.add(lesson)
        purchase = Purchase(
            user_id=user_id,
            course_id=course.id,
            status="approved",
            amount_cop=100000,
        )
        db.session.add(purchase)
        db.session.commit()
        return token, lesson.id


def test_get_progress_empty(client, app):
    rv = client.post(
        "/api/auth/register",
        data=json.dumps({"email": "empty@test.com", "name": "E", "password": "password123"}),
        content_type="application/json",
    )
    token = rv.get_json()["token"]
    rv2 = client.get("/api/progress", headers={"Authorization": f"Bearer {token}"})
    assert rv2.status_code == 200
    assert rv2.get_json() == []


def test_mark_completed(client, app):
    token, lesson_id = _setup(client, app)
    rv = client.post(
        "/api/progress",
        data=json.dumps({"lesson_id": lesson_id, "watch_percentage": 95, "completed": True}),
        content_type="application/json",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert rv.status_code == 200
    data = rv.get_json()
    assert data["completed"] is True
    assert data["watch_percentage"] == 95


def test_upsert_no_duplicate(client, app):
    token, lesson_id = _setup(client, app)

    def post_progress(**kwargs):
        return client.post(
            "/api/progress",
            data=json.dumps({"lesson_id": lesson_id, **kwargs}),
            content_type="application/json",
            headers={"Authorization": f"Bearer {token}"},
        )

    post_progress(watch_percentage=50, completed=False)
    post_progress(watch_percentage=90, completed=True)

    rv = client.get("/api/progress", headers={"Authorization": f"Bearer {token}"})
    rows = rv.get_json()
    assert len(rows) == 1
    assert rows[0]["completed"] is True
    assert rows[0]["watch_percentage"] == 90
