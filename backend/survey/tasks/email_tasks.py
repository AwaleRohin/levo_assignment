from flask_mail import Message
from survey.app import mail, celery, app
from survey.utils.utils import get_logger

logger = get_logger()


@celery.task(bind=True, max_retries=5, default_retry_delay=60)
def send_email_task(self, subject, recipients, body, html=None):
    """
    Celery task to send an email with retry logic.

    This task sends a plain text or HTML email to the specified recipients.
    Currently, it supports sending to a single email address using the SMTP provider.
    If the email fails to send due to an exception (e.g., SMTP error),
    it will automatically retry with exponential backoff.

    Args:
        self (Task): Reference to the bound Celery task instance.
        subject (str): The subject line of the email.
        recipients (str or list): Email address(es) to send the message to.
        body (str): Plain text content of the email.
        html (str, optional): Optional HTML content for the email.

    Raises:
        Retry: Retries the task up to 5 times with exponential backoff if sending fails.
    """
    try:
        with app.app_context():
            msg = Message(subject, recipients=[recipients], body=body, html=html)
            mail.send(msg)
            logger.info(f"Email sent successfully to {recipients}")
    except Exception as e:
        logger.error(f"Error sending email: {e}, retrying...")
        raise self.retry(exc=e, countdown=2 ** self.request.retries * 60)