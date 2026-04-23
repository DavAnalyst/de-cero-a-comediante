from datetime import datetime
from flask import Blueprint, request, jsonify, g
from ..extensions import db
from ..models import Progress, Lesson, Purchase
from ..utils.auth import require_auth

progress_bp = Blueprint("progress", __name__)


@progress_bp.route("", methods=["GET"])
@require_auth
def get_progress():
    user = g.current_user
    rows = Progress.query.filter_by(user_id=user.id).all()
    return jsonify([r.to_dict() for r in rows])


@progress_bp.route("", methods=["POST"])
@require_auth
def update_progress():
    user = g.current_user
    data = request.get_json(silent=True) or {}
    lesson_id = data.get("lesson_id")
    watch_percentage = data.get("watch_percentage", 0)
    completed = data.get("completed", False)

    if not lesson_id:
        return jsonify({"error": "lesson_id is required"}), 400

    lesson = Lesson.query.get_or_404(lesson_id)

    enrolled = Purchase.query.filter_by(
        user_id=user.id, course_id=lesson.course_id, status="approved"
    ).first()
    if not enrolled:
        return jsonify({"error": "Not enrolled in this course"}), 403

    # Upsert
    prog = Progress.query.filter_by(user_id=user.id, lesson_id=lesson_id).first()
    if prog is None:
        prog = Progress(user_id=user.id, lesson_id=lesson_id)
        db.session.add(prog)

    prog.watch_percentage = max(prog.watch_percentage, int(watch_percentage))
    if completed and not prog.completed:
        prog.completed = True
        prog.completed_at = datetime.utcnow()

    db.session.commit()
    return jsonify(prog.to_dict())
