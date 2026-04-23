import time
import hmac
import hashlib
from flask import current_app


def get_signed_url(provider: str, video_id: str, expires_in: int = 3600) -> str:
    if provider == "cloudinary":
        return _cloudinary_signed_url(video_id, expires_in)
    elif provider == "bunny":
        return _bunny_signed_url(video_id, expires_in)
    raise ValueError(f"Unknown video provider: {provider}")


def _cloudinary_signed_url(public_id: str, expires_in: int) -> str:
    import cloudinary
    import cloudinary.utils

    cloudinary.config(
        cloud_name=current_app.config["CLOUDINARY_CLOUD_NAME"],
        api_key=current_app.config["CLOUDINARY_API_KEY"],
        api_secret=current_app.config["CLOUDINARY_API_SECRET"],
    )
    expires_at = int(time.time()) + expires_in
    url, _ = cloudinary.utils.cloudinary_url(
        public_id,
        resource_type="video",
        type="authenticated",
        expires_at=expires_at,
        sign_url=True,
    )
    return url


def _bunny_signed_url(video_id: str, expires_in: int) -> str:
    cdn_url = current_app.config["BUNNY_CDN_URL"].rstrip("/")
    api_key = current_app.config["BUNNY_API_KEY"]
    expires_at = int(time.time()) + expires_in
    path = f"/{video_id}"
    token_raw = f"{api_key}{path}{expires_at}"
    token = hashlib.sha256(token_raw.encode()).digest()
    import base64
    token_b64 = base64.b64encode(token).decode().replace("+", "-").replace("/", "_").replace("=", "")
    return f"{cdn_url}{path}?token={token_b64}&expires={expires_at}"
