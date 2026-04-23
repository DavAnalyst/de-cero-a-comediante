import json
import hashlib
import hmac
from app.extensions import db
from app.models import Course, Purchase


def _make_payload(reference, status="APPROVED"):
    return {
        "event": "transaction.updated",
        "data": {
            "transaction": {
                "id": "wompi_txn_001",
                "reference": reference,
                "status": status,
            }
        },
    }


def _sign_payload(payload_dict, secret):
    canonical = json.dumps(payload_dict, sort_keys=True, separators=(",", ":"))
    return hmac.new(secret.encode(), canonical.encode(), hashlib.sha256).hexdigest()


def _create_pending_purchase(app):
    rv_reg = None
    with app.app_context():
        course = Course(title="Wompi Course", price_cop=299000, is_published=True)
        db.session.add(course)
        db.session.flush()

        from app.models import User
        from app.extensions import bcrypt
        user = User(
            email="buyer@test.com",
            name="Buyer",
            password_hash=bcrypt.generate_password_hash("password123").decode(),
        )
        db.session.add(user)
        db.session.flush()

        purchase = Purchase(
            user_id=user.id,
            course_id=course.id,
            amount_cop=299000,
            status="pending",
        )
        db.session.add(purchase)
        db.session.commit()
        return purchase.id


def test_webhook_approved_valid_signature(client, app):
    purchase_id = _create_pending_purchase(app)
    secret = app.config["WOMPI_EVENTS_SECRET"]
    payload = _make_payload(purchase_id, "APPROVED")
    checksum = _sign_payload(payload, secret)

    rv = client.post(
        "/api/webhook/wompi",
        data=json.dumps(payload),
        content_type="application/json",
        headers={"X-Event-Checksum": checksum},
    )
    assert rv.status_code == 200

    with app.app_context():
        p = Purchase.query.get(purchase_id)
        assert p.status == "approved"
        assert p.wompi_transaction_id == "wompi_txn_001"


def test_webhook_invalid_signature(client, app):
    purchase_id = _create_pending_purchase(app)
    payload = _make_payload(purchase_id, "APPROVED")

    rv = client.post(
        "/api/webhook/wompi",
        data=json.dumps(payload),
        content_type="application/json",
        headers={"X-Event-Checksum": "invalidsignature"},
    )
    assert rv.status_code == 400

    with app.app_context():
        p = Purchase.query.get(purchase_id)
        assert p.status == "pending"
