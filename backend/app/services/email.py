from flask import current_app
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail


def _send(to_email: str, subject: str, html_content: str) -> None:
    api_key = current_app.config.get("SENDGRID_API_KEY")
    from_email = current_app.config.get("FROM_EMAIL")
    if not api_key:
        return  # silently skip in dev when not configured
    message = Mail(
        from_email=from_email,
        to_emails=to_email,
        subject=subject,
        html_content=html_content,
    )
    client = SendGridAPIClient(api_key)
    client.send(message)


def send_welcome_email(to_email: str, name: str) -> None:
    subject = "Bienvenido/a a De Cero a Comediante"
    html_content = f"""
    <h1>Hola, {name}!</h1>
    <p>Tu cuenta ha sido creada exitosamente en <strong>De Cero a Comediante</strong>.</p>
    <p>Estamos emocionados de acompañarte en este viaje al stand-up comedy.</p>
    <p>Si tienes preguntas, responde a este correo.</p>
    """
    _send(to_email, subject, html_content)


def send_purchase_confirmation(to_email: str, name: str, course_title: str) -> None:
    subject = f"Confirmación de compra: {course_title}"
    html_content = f"""
    <h1>Gracias por tu compra, {name}!</h1>
    <p>Tu pago para <strong>{course_title}</strong> fue aprobado.</p>
    <p>Ya puedes acceder al curso desde tu dashboard.</p>
    """
    _send(to_email, subject, html_content)
