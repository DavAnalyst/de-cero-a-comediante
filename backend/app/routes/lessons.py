from flask import Blueprint, jsonify, g
from ..models import Lesson, Purchase
from ..utils.auth import require_auth
from ..services.video import get_signed_url

lessons_bp = Blueprint("lessons", __name__)


@lessons_bp.route("/<lesson_id>", methods=["GET"])
@require_auth
def get_lesson(lesson_id):
    lesson = Lesson.query.get_or_404(lesson_id)
    user = g.current_user

    enrolled = Purchase.query.filter_by(
        user_id=user.id, course_id=lesson.course_id, status="approved"
    ).first()
    if not enrolled:
        return jsonify({"error": "You are not enrolled in this course"}), 403

    data = lesson.to_dict(include_video=True)

    if lesson.video_id:
        try:
            data["video_url"] = get_signed_url(lesson.video_provider, lesson.video_id)
        except Exception as e:
            data["video_url"] = None
            data["video_error"] = str(e)

    return jsonify(data)
