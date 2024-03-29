from fastapi import BackgroundTasks
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from dotenv import load_dotenv
import os
load_dotenv()

conf = ConnectionConfig(
    MAIL_USERNAME = os.getenv("MAIL_USERNAME"),
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD"),
    MAIL_FROM = "uccusodirty@gmail.com",
    MAIL_PORT = 587,
    MAIL_SERVER = "smtp.gmail.com",
    MAIL_TLS = True,
    MAIL_SSL = False,
    USE_CREDENTIALS = True,
)

async def send_email(subject: str, email_to: str, quiz_name: dict):

    body = "Your quiz: " + quiz_name + " has been generated. Please check it on the application."

    message = MessageSchema(
        subject=subject,
        recipients=[email_to],
        body=body,
    )

    fm = FastMail(conf)

    await fm.send_message(message)