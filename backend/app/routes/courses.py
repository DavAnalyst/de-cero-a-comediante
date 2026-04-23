from flask import Blueprint, jsonify, g
from ..models import Course, Lesson, Progress, Purchase
from ..utils.auth import require_auth
from ..extensions import db

courses_bp = Blueprint("courses", __name__)


def _get_optional_user():
    """Return the current user from g if set, else None."""
    return getattr(g, "current_user", None)


def _is_enrolled(user, course_id):
    if user is None:
        return False
    return Purchase.query.filter_by(
        user_id=user.id, course_id=course_id, status="approved"
    ).first() is not None


def _course_progress_pct(user, course_id):
    if user is None:
        return 0
    total = Lesson.query.filter_by(course_id=course_id).count()
    if total == 0:
        return 0
    completed = (
        db.session.query(Progress)
        .join(Lesson, Progress.lesson_id == Lesson.id)
        .filter(
            Progress.user_id == user.id,
            Lesson.course_id == course_id,
            Progress.completed == True,
        )
        .count()
    )
    return round(completed / total * 100)


@courses_bp.route("", methods=["GET"])
def list_courses():
    courses = Course.query.filter_by(is_published=True).all()
    return jsonify([c.to_dict() for c in courses])


@courses_bp.route("/<course_id>", methods=["GET"])
def course_detail(course_id):
    course = Course.query.filter_by(id=course_id, is_published=True).first_or_404()
    data = course.to_dict()

    # Optionally enrich with enrollment data if JWT present
    from ..utils.auth import _decode_token
    from ..models import User
    payload, _ = _decode_token()
    user = User.query.get(payload["sub"]) if payload else None

    if user:
        enrolled = _is_enrolled(user, course_id)
        data["is_enrolled"] = enrolled
        data["progress_pct"] = _course_progress_pct(user, course_id) if enrolled else 0

    return jsonify(data)


@courses_bp.route("/<course_id>/lessons", methods=["GET"])
@require_auth
def course_lessons(course_id):
    course = Course.query.filter_by(id=course_id, is_published=True).first_or_404()
    user = g.current_user

    if not _is_enrolled(user, course_id):
        return jsonify({"error": "You are not enrolled in this course"}), 403

    lessons = (
        Lesson.query.filter_by(course_id=course_id)
        .order_by(Lesson.module_num, Lesson.order_in_module)
        .all()
    )

    # Fetch user progress in bulk
    lesson_ids = [l.id for l in lessons]
    progress_rows = Progress.query.filter(
        Progress.user_id == user.id,
        Progress.lesson_id.in_(lesson_ids),
    ).all()
    progress_map = {p.lesson_id: p for p in progress_rows}

    # Group by module
    modules = {}
    for lesson in lessons:
        key = lesson.module_num
        if key not in modules:
            modules[key] = {
                "module_num": lesson.module_num,
                "module_name": lesson.module_name,
                "lessons": [],
            }
        lesson_data = lesson.to_dict()
        prog = progress_map.get(lesson.id)
        lesson_data["completed"] = prog.completed if prog else False
        lesson_data["watch_percentage"] = prog.watch_percentage if prog else 0
        modules[key]["lessons"].append(lesson_data)

    return jsonify({"course": course.to_dict(), "modules": list(modules.values())})
