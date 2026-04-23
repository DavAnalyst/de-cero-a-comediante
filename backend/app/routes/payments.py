from datetime import datetime
from flask import Blueprint, request, jsonify, g, current_app
from ..extensions import db
from ..models import Purchase, Course
from ..utils.auth import require_auth
from ..services.wompi import generate_integrity_signature, verify_webhook_signature

payments_bp = Blueprint("payments", __name__)


@payments_bp.route("/checkout/wompi", methods=["POST"])
@require_auth
def checkout_wompi():
    user = g.current_user
    data = request.get_json(silent=True) or {}
    course_id = data.get("course_id")

    if not course_id:
        return jsonify({"error": "course_id is required"}), 400

    course = Course.query.filter_by(id=course_id, is_published=True).first_or_404()

    # Check not already purchased
    existing = Purchase.query.filter_by(
        user_id=user.id, course_id=course_id, status="approved"
    ).first()
    if existing:
        return jsonify({"error": "You already have access to this course"}), 409

    amount_in_cents = int(float(course.price_cop) * 100)
    currency = "COP"
    public_key = current_app.config["WOMPI_PUBLIC_KEY"]
    integrity_secret = current_app.config["WOMPI_INTEGRITY_SECRET"]

    # Create pending purchase — its id is the Wompi reference
    purchase = Purchase(
        user_id=user.id,
        course_id=course_id,
        amount_cop=course.price_cop,
        status="pending",
    )
    db.session.add(purchase)
    db.session.commit()

    signature = generate_integrity_signature(
        purchase.id, amount_in_cents, currency, integrity_secret
    )

    return jsonify(
        {
            "public_key": public_key,
            "amount_in_cents": amount_in_cents,
            "currency": currency,
            "reference": purchase.id,
            "signature_integrity": signature,
        }
    )


@payments_bp.route("/webhook/wompi", methods=["POST"])
def webhook_wompi():
    payload = request.get_json(silent=True)
    if not payload:
        return jsonify({"error": "Invalid payload"}), 400

    checksum = request.headers.get("X-Event-Checksum", "")
    events_secret = current_app.config["WOMPI_EVENTS_SECRET"]

    if not verify_webhook_signature(payload, checksum, events_secret):
        return jsonify({"error": "Invalid signature"}), 400

    event = payload.get("event", "")
    if event != "transaction.updated":
        return jsonify({"status": "ignored"}), 200

    transaction = payload.get("data", {}).get("transaction", {})
    status = transaction.get("status", "")
    reference = transaction.get("reference", "")
    transaction_id = transaction.get("id", "")

    purchase = Purchase.query.get(reference)
    if not purchase:
        return jsonify({"error": "Purchase not found"}), 404

    purchase.wompi_transaction_id = transaction_id

    if status == "APPROVED":
        purchase.status = "approved"
        purchase.approved_at = datetime.utcnow()
        # Send purchase confirmation email (non-blocking)
        try:
            from ..services.email import send_purchase_confirmation
            from ..models import User, Course
            user = User.query.get(purchase.user_id)
            course = Course.query.get(purchase.course_id)
            if user and course:
                send_purchase_confirmation(user.email, user.name, course.title)
        except Exception:
            pass
    elif status in ("DECLINED", "VOIDED", "ERROR"):
        purchase.status = status.lower() if status.lower() in ("declined", "voided") else "declined"

    db.session.commit()
    return jsonify({"status": "ok"})
