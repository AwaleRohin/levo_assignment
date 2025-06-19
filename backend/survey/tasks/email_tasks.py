from flask_mail import Message
from survey.app import mail, celery, app


@celery.task
def send_email_task(subject, recipients, body, html=None):
    with app.app_context():
        msg = Message(subject, recipients=[recipients], body=body, html=html)
        mail.send(msg)
        print(f"Sent email to {recipients}")
