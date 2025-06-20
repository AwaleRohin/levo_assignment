from flask_mail import Message
from survey.app import mail, celery, app
from survey.utils.utils import get_logger

logger = get_logger()


@celery.task(bind=True, max_retries=5, default_retry_delay=60)
def send_email_task(self, subject, recipients, body, html=None):
    try:
        with app.app_context():
            msg = Message(subject, recipients=[recipients], body=body, html=html)
            mail.send(msg)
            logger.info(f"Email sent successfully to {recipients}")
    except Exception as e:
        logger.error(f"Error sending email: {e}, retrying...")
        raise self.retry(exc=e, countdown=2 ** self.request.retries * 60)