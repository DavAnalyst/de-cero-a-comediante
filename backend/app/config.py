import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-insecure")
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "dev-jwt-insecure")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    CLOUDINARY_CLOUD_NAME = os.environ.get("CLOUDINARY_CLOUD_NAME", "")
    CLOUDINARY_API_KEY = os.environ.get("CLOUDINARY_API_KEY", "")
    CLOUDINARY_API_SECRET = os.environ.get("CLOUDINARY_API_SECRET", "")

    BUNNY_STORAGE_ZONE = os.environ.get("BUNNY_STORAGE_ZONE", "")
    BUNNY_API_KEY = os.environ.get("BUNNY_API_KEY", "")
    BUNNY_CDN_URL = os.environ.get("BUNNY_CDN_URL", "")

    WOMPI_PUBLIC_KEY = os.environ.get("WOMPI_PUBLIC_KEY", "")
    WOMPI_PRIVATE_KEY = os.environ.get("WOMPI_PRIVATE_KEY", "")
    WOMPI_INTEGRITY_SECRET = os.environ.get("WOMPI_INTEGRITY_SECRET", "")
    WOMPI_EVENTS_SECRET = os.environ.get("WOMPI_EVENTS_SECRET", "")

    SENDGRID_API_KEY = os.environ.get("SENDGRID_API_KEY", "")
    FROM_EMAIL = os.environ.get("FROM_EMAIL", "noreply@example.com")

    FRONTEND_URL = os.environ.get("FRONTEND_URL", "http://localhost:3000")


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", "sqlite:///dev.db"
    )


class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")
    SQLALCHEMY_POOL_PRE_PING = True
    SQLALCHEMY_POOL_RECYCLE = 280
    SQLALCHEMY_POOL_SIZE = 5
    SQLALCHEMY_MAX_OVERFLOW = 2


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    JWT_SECRET_KEY = "test-jwt-secret"
    SECRET_KEY = "test-secret"
    WTF_CSRF_ENABLED = False


config_by_name = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
}
