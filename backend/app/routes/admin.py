from flask import Blueprint, request, jsonify, g
from ..extensions import db
from ..models import Course, Lesson, User
from ..utils.auth import require_admin

admin_bp = Blueprint("admin", __name__)


# ─── Courses ────────────────────────────────────────────────────────────────

@admin_bp.route("/courses", methods=["GET"])
@require_admin
def list_courses():
    courses = Course.query.order_by(Course.created_at.desc()).all()
    return jsonify([c.to_dict() for c in courses])


@admin_bp.route("/courses", methods=["POST"])
@require_admin
def create_course():
    data = request.get_json(silent=True) or {}
    title = (data.get("title") or "").strip()
    if not title:
        return jsonify({"error": "title is required"}), 400

    course = Course(
        title=title,
        description=data.get("description"),
        price_cop=data.get("price_cop"),
        is_published=data.get("is_published", False),
    )
    db.session.add(course)
    db.session.commit()
    return jsonify(course.to_dict()), 201


@admin_bp.route("/courses/<course_id>", methods=["PUT"])
@require_admin
def update_course(course_id):
    course = Course.query.get_or_404(course_id)
    data = request.get_json(silent=True) or {}

    if "title" in data:
        course.title = data["title"].strip()
    if "description" in data:
        course.description = data["description"]
    if "price_cop" in data:
        course.price_cop = data["price_cop"]
    if "is_published" in data:
        course.is_published = bool(data["is_published"])

    db.session.commit()
    return jsonify(course.to_dict())


# ─── Lessons ────────────────────────────────────────────────────────────────

@admin_bp.route("/lessons", methods=["GET"])
@require_admin
def list_lessons():
    course_id = request.args.get("course_id")
    query = Lesson.query
    if course_id:
        query = query.filter_by(course_id=course_id)
    lessons = query.order_by(Lesson.module_num, Lesson.order_in_module).all()
    return jsonify([l.to_dict(include_video=True) for l in lessons])


@admin_bp.route("/lessons", methods=["POST"])
@require_admin
def create_lesson():
    data = request.get_json(silent=True) or {}
    required = ["course_id", "module_num", "order_in_module", "title"]
    missing = [f for f in required if not data.get(f)]
    if missing:
        return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400

    # Validate course exists
    Course.query.get_or_404(data["course_id"])

    lesson = Lesson(
        course_id=data["course_id"],
        module_num=int(data["module_num"]),
        module_name=data.get("module_name"),
        order_in_module=int(data["order_in_module"]),
        title=data["title"].strip(),
        description=data.get("description"),
        video_provider=data.get("video_provider", "cloudinary"),
        video_id=data.get("video_id"),
        duration_seconds=data.get("duration_seconds"),
        has_exercise=data.get("has_exercise", False),
        exercise_content=data.get("exercise_content"),
    )
    db.session.add(lesson)
    db.session.commit()
    return jsonify(lesson.to_dict(include_video=True)), 201


@admin_bp.route("/lessons/<lesson_id>", methods=["PUT"])
@require_admin
def update_lesson(lesson_id):
    lesson = Lesson.query.get_or_404(lesson_id)
    data = request.get_json(silent=True) or {}

    fields = [
        "module_num", "module_name", "order_in_module", "title",
        "description", "video_provider", "video_id", "duration_seconds",
        "has_exercise", "exercise_content",
    ]
    for field in fields:
        if field in data:
            setattr(lesson, field, data[field])

    db.session.commit()
    return jsonify(lesson.to_dict(include_video=True))


# ─── Users ──────────────────────────────────────────────────────────────────

@admin_bp.route("/users", methods=["GET"])
@require_admin
def list_users():
    users = User.query.order_by(User.created_at.desc()).all()
    return jsonify([u.to_dict() for u in users])
