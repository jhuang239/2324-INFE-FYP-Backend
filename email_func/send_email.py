from fastapi import BackgroundTasks
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from dotenv import load_dotenv
import os
load_dotenv()

conf = ConnectionConfig(
    MAIL_USERNAME = os.getenv("MAIL_USERNAME"),
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD"),
    MAIL_FROM = "uccusodirty@gmail.com",
    MAIL_PORT = 465,
    MAIL_SERVER = "smtp.gmail.com",
    MAIL_FROM_NAME="Quiz App",
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
    USE_CREDENTIALS = True,
    VALIDATE_CERTS = True
)

def send_email_background(background_tasks: BackgroundTasks, subject: str, email_to: str, quiz_name: dict, type: str):
    html = ""

    if type == "quiz":
        html = """<p>Your quiz: """ + quiz_name + """ has been generated. Please check it on the application.</p>"""
    elif type == "U_E":
        html = """<p>The file is successfully uploaded and embedded</p>"""
    else :
        html = """<p>Folder and related files successfully removed</p>"""

    message = MessageSchema(
        subject=subject,
        recipients=[email_to],
        body=html,
        subtype=MessageType.html
    )

    fm = FastMail(conf)
    background_tasks.add_task(fm.send_message, message)