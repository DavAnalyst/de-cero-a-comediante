import uuid
from datetime import datetime
from .extensions import db


def _uuid():
    return str(uuid.uuid4())


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.String(36), primary_key=True, default=_uuid)
    email = db.Column(db.String(255), unique=True, nullable=False)
    name = db.Column(db.String(255), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    purchases = db.relationship("Purchase", backref="user", lazy=True)
    progress = db.relationship("Progress", backref="user", lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "email": self.email,
            "name": self.name,
            "is_admin": self.is_admin,
            "created_at": self.created_at.isoformat(),
        }


class Course(db.Model):
    __tablename__ = "courses"

    id = db.Column(db.String(36), primary_key=True, default=_uuid)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    price_cop = db.Column(db.Numeric(10, 2))
    is_published = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    lessons = db.relationship(
        "Lesson", backref="course", lazy=True, cascade="all, delete-orphan"
    )
    purchases = db.relationship("Purchase", backref="course", lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "price_cop": float(self.price_cop) if self.price_cop else None,
            "is_published": self.is_published,
            "created_at": self.created_at.isoformat(),
        }


class Lesson(db.Model):
    __tablename__ = "lessons"

    id = db.Column(db.String(36), primary_key=True, default=_uuid)
    course_id = db.Column(
        db.String(36), db.ForeignKey("courses.id", ondelete="CASCADE"), nullable=False
    )
    module_num = db.Column(db.Integer, nullable=False)
    module_name = db.Column(db.String(255))
    order_in_module = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    video_provider = db.Column(
        db.Enum("cloudinary", "bunny"), default="cloudinary", nullable=False
    )
    video_id = db.Column(db.String(500))
    duration_seconds = db.Column(db.Integer)
    has_exercise = db.Column(db.Boolean, default=False, nullable=False)
    exercise_content = db.Column(db.Text)

    progress = db.relationship("Progress", backref="lesson", lazy=True)

    def to_dict(self, include_video=False):
        data = {
            "id": self.id,
            "course_id": self.course_id,
            "module_num": self.module_num,
            "module_name": self.module_name,
            "order_in_module": self.order_in_module,
            "title": self.title,
            "description": self.description,
            "video_provider": self.video_provider,
            "duration_seconds": self.duration_seconds,
            "has_exercise": self.has_exercise,
        }
        if include_video:
            data["video_id"] = self.video_id
            data["exercise_content"] = self.exercise_content
        return data


class Progress(db.Model):
    __tablename__ = "progress"

    id = db.Column(db.String(36), primary_key=True, default=_uuid)
    user_id = db.Column(
        db.String(36), db.ForeignKey("users.id"), nullable=False
    )
    lesson_id = db.Column(
        db.String(36), db.ForeignKey("lessons.id"), nullable=False
    )
    watch_percentage = db.Column(db.Integer, default=0, nullable=False)
    completed = db.Column(db.Boolean, default=False, nullable=False)
    completed_at = db.Column(db.DateTime, nullable=True)

    __table_args__ = (db.UniqueConstraint("user_id", "lesson_id", name="uq_user_lesson"),)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "lesson_id": self.lesson_id,
            "watch_percentage": self.watch_percentage,
            "completed": self.completed,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }


class Purchase(db.Model):
    __tablename__ = "purchases"

    id = db.Column(db.String(36), primary_key=True, default=_uuid)
    user_id = db.Column(
        db.String(36), db.ForeignKey("users.id"), nullable=False
    )
    course_id = db.Column(
        db.String(36), db.ForeignKey("courses.id"), nullable=False
    )
    wompi_transaction_id = db.Column(db.String(255))
    status = db.Column(
        db.Enum("pending", "approved", "declined", "voided"),
        default="pending",
        nullable=False,
    )
    amount_cop = db.Column(db.Numeric(10, 2))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    approved_at = db.Column(db.DateTime, nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "course_id": self.course_id,
            "wompi_transaction_id": self.wompi_transaction_id,
            "status": self.status,
            "amount_cop": float(self.amount_cop) if self.amount_cop else None,
            "created_at": self.created_at.isoformat(),
            "approved_at": self.approved_at.isoformat() if self.approved_at else None,
        }
