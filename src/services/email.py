from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from fastapi_mail.errors import ConnectionErrors
from pydantic import EmailStr
from src.conf.config import settings

conf = ConnectionConfig(
    MAIL_USERNAME=settings.SMTP_USER,
    MAIL_PASSWORD=settings.SMTP_PASSWORD,
    MAIL_FROM=settings.SMTP_USER,
    MAIL_PORT=settings.SMTP_PORT,
    MAIL_SERVER=settings.SMTP_HOST,
    MAIL_FROM_NAME="Phonebook App",
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=False,
)


async def send_verification_email(email: EmailStr, token: str):
    verify_url = f"http://127.0.0.1:8000/auth/verify/{token}"

    message = MessageSchema(
        subject="Email Verification",
        recipients=[email],
        body=(
            f"Hi 👋, please verify your email by clicking the following link: "
            f"{verify_url}"
        ),
        subtype="plain"
    )

    fm = FastMail(conf)
    try:
        await fm.send_message(message)
    except ConnectionErrors as e:
        print(f"SMTP error: {e}")
