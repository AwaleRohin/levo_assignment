from survey.app import db, celery
from survey.models.models import Survey

from survey.utils.utils import get_logger

logger = get_logger()


@celery.task
def publish_survey_task(survey_id):
    """
    Celery task to publish a scheduled survey.

    This task is typically scheduled using `apply_async` with a `countdown` delay
    from the survey creation or update logic.

    It checks if the survey exists, is unpublished, and has a scheduled time.
    If so, it marks the survey as published and clears the scheduled time.

    Args:
        survey_id (int): The ID of the survey to publish.
    """
    survey = Survey.query.get(survey_id)

    if survey and not survey.published and survey.scheduled_time:
        survey.published = True
        survey.scheduled_time = None
        db.session.commit()
        logger.info(f"Survey {survey_id} has been published.")
    else:
        logger.error(
            f"Survey {survey_id} was already published or unscheduled before task ran.")
