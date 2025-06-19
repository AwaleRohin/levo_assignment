from survey.app import db, celery
from survey.models.models import Survey


@celery.task
def publish_survey_task(survey_id):
    survey = Survey.query.get(survey_id)

    if survey and not survey.published and survey.scheduled_time:
        survey.published = True
        survey.scheduled_time = None
        db.session.commit()
        print(f"Survey {survey_id} has been published.")
    else:
        print(f"Survey {survey_id} was already published or unscheduled before task ran.")
