import hashlib
import hmac
import json


def generate_integrity_signature(
    reference: str,
    amount_in_cents: int,
    currency: str,
    integrity_secret: str,
) -> str:
    """SHA-256 of reference + amount_in_cents + currency + integrity_secret (Wompi spec)."""
    raw = f"{reference}{amount_in_cents}{currency}{integrity_secret}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def verify_webhook_signature(
    payload_dict: dict,
    checksum_header: str,
    events_secret: str,
) -> bool:
    """Verify Wompi webhook HMAC-SHA256 signature.

    Wompi sends: HMAC-SHA256(events_secret, json_body_sorted_keys)
    """
    if not checksum_header or not events_secret:
        return False

    try:
        # Wompi signs the raw JSON with keys in the order they appear; we reproduce
        # the canonical form by re-serializing with sorted keys.
        canonical = json.dumps(payload_dict, sort_keys=True, separators=(",", ":"))
        expected = hmac.new(
            events_secret.encode("utf-8"),
            canonical.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        return hmac.compare_digest(expected, checksum_header)
    except Exception:
        return False
