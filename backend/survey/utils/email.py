from threading import Thread
from flask_mail import Mail, Message

from survey.app import mail, app


def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def send_email(subject, recipients_str, body, html=None):
    recipients = [email.strip() for email in recipients_str.split(',') if email.strip()]
    print(recipients)
    msg = Message(subject, recipients=recipients, body=body, html=html)
    Thread(target=send_async_email, args=(app, msg)).start()
