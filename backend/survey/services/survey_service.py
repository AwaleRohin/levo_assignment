import csv
import ast
from io import TextIOWrapper
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from survey.models.models import Survey, Question, Response
from survey.utils.exceptions import SurveyNotFoundError
from datetime import datetime, timezone
from survey.tasks.schedule_publish import publish_survey_task
from survey.utils.utils import convert_to_utc, get_logger

logger = get_logger()

class SurveyService:
    """Service class that handles business logic related to surveys, questions, and responses."""
    def __init__(self, session: Session):
        """
        Initialize the SurveyService with a SQLAlchemy session.

        Args:
            session (Session): SQLAlchemy session for database operations.
        """
        self.session = session

    def create_survey(self, data: Dict[str, Any], questions_data: List[Dict[str, Any]]) -> Survey:
        """
        Create a new survey with associated questions.

        If `published` is True, the survey is published immediately.
        If `published` is False and a `scheduled_time` is provided, the survey is scheduled for future publishing.
        IF `published` is False and a `scheduled_time` is not provided,, the survey is saved as draft.

        Args:
            data (dict): Survey data including title, description, published flag, etc.
            questions_data (List[dict]): List of question data dictionaries.

        Returns:
            Survey: The created Survey object.
        """
        published = data.get("published", True)
        scheduled_time_str = data.get("scheduled_time")
        timezone_name = data.pop("timezone", "UTC")

        if published:
            # If published is True, scheduled_time must be None
            data["scheduled_time"] = None
            logger.debug("Survey is marked as published; clearing scheduled_time")
        elif not scheduled_time_str:
            # If published is False and no scheduled_time, keep both
            data["scheduled_time"] = None
            logger.debug("Survey is not published and no scheduled_time provided; setting scheduled_time to None")

        survey = Survey(**data)
        self.session.add(survey)
        self.session.flush()

        for q_data in questions_data:
            question = Question(
                survey_id=survey.id,
                text=q_data.get("text"),
                type=q_data.get("type"),
                options=q_data.get("options"),
                required=q_data.get("required", False),
                order=q_data.get("order", 0),
            )
            self.session.add(question)

        self.session.commit()
        self.session.refresh(survey)
        if not published and scheduled_time_str:
            scheduled_time_utc = convert_to_utc(scheduled_time_str, timezone_name)
            delay = (scheduled_time_utc - datetime.now().replace(tzinfo=timezone.utc)).total_seconds()
            if delay > 0:
                publish_survey_task.apply_async(args=[survey.id], countdown=delay)
                logger.info(f"Survey id={survey.id} scheduled for publishing in {delay} seconds (UTC time: {scheduled_time_utc})")
            else:
                logger.warning(f"Scheduled time for survey id={survey.id} is in the past; skipping scheduling and and publishing it")
                survey.published = True
                survey.scheduled_time = None
                self.session.commit()
        return survey

    def get_survey(self, survey_id: int) -> Survey:
        """
        Retrieve a survey by its ID.

        Args:
            survey_id (int): The ID of the survey to retrieve.

        Returns:
            Survey: The Survey object.

        Raises:
            SurveyNotFoundError: If the survey with the given ID does not exist.
        """
        survey = self.session.query(Survey).filter(Survey.id == survey_id).first()
        if not survey:
            logger.warning(f"Survey not found for id={survey_id}")
            raise SurveyNotFoundError(survey_id)
        return survey

    def get_all_surveys(self) -> List[Survey]:
        """
        Retrieve all surveys from the database.

        Returns:
            List[Survey]: A list of all Survey objects.
        """
        return self.session.query(Survey).all()

    def update_survey(self, survey_id: int, data: Dict[str, Any], questions_data: List[Dict[str, Any]]) -> Survey:
        """
        Update a survey and replace its questions.

        If the survey is unpublished and `scheduled_time` is provided, it will be scheduled.
        All existing questions will be deleted and replaced with the new ones.

        Args:
            survey_id (int): The ID of the survey to update.
            data (dict): Updated survey data.
            questions_data (List[dict]): List of new questions.

        Returns:
            Survey: The updated Survey object.
        """
        survey = self.get_survey(survey_id)
        published = data.get("published", survey.published or False)
        scheduled_time_str = data.get("scheduled_time", None)
        timezone_name = data.pop("timezone", "UTC")

        if published:
            survey.published = True
            survey.scheduled_time = None
        elif not published and scheduled_time_str:
            survey.published = False
            survey.scheduled_time = scheduled_time_str
            scheduled_time_utc = convert_to_utc(scheduled_time_str, timezone_name)
            delay = (scheduled_time_utc - datetime.now().replace(tzinfo=timezone.utc)).total_seconds()
            if delay > 0:
                publish_survey_task.apply_async(args=[survey.id], countdown=delay)
                logger.info(f"Survey id={survey.id} scheduled for publishing in {delay} seconds (UTC time: {scheduled_time_utc})")
            else:
                logger.info(f"Scheduled time for survey id={survey.id} is in the past; skipping scheduling and publishing it")
                survey.published = True
                survey.scheduled_time = None
        else:
            survey.published = False
            survey.scheduled_time = None

        # Update survey fields
        for key, value in data.items():
            if hasattr(survey, key):
                setattr(survey, key, value)

        # Delete old questions
        self.session.query(Question).filter(Question.survey_id == survey.id).delete()

        # Add new questions
        for q_data in questions_data:
            question = Question(
                survey_id=survey.id,
                text=q_data.get("text"),
                type=q_data.get("type"),
                options=q_data.get("options"),
                required=q_data.get("required", False),
                order=q_data.get("order", 0),
            )
            self.session.add(question)

        self.session.commit()
        return survey

    def delete_survey(self, survey_id: int) -> None:
        """
        Delete a survey and cascade delete its questions and responses.

        Args:
            survey_id (int): The ID of the survey to delete.
        """
        survey = self.get_survey(survey_id)
        
        # Delete related questions and responses
        self.session.query(Question).filter(Question.survey_id == survey.id).delete()
        self.session.query(Response).filter(Response.survey_id == survey.id).delete()
        
        self.session.delete(survey)
        logger.info(f"Deleted survey object with id={survey_id}")
        self.session.commit()

    def get_survey_stats(self, survey_id: int) -> Dict[str, Any]:
        """
        Retrieve statistics for a single survey.

        Statistics include total number of questions, responses, and creation time.

        Args:
            survey_id (int): The ID of the survey.

        Returns:
            dict: A dictionary with statistics for the given survey.
        """
        survey = self.get_survey(survey_id)
        
        response_count = self.session.query(Response).filter(Response.survey_id == survey_id).count()
        question_count = self.session.query(Question).filter(Question.survey_id == survey_id).count()
        
        return {
            'survey_id': survey_id,
            'title': survey.title,
            'total_responses': response_count,
            'total_questions': question_count,
            'created_at': survey.created_at.isoformat() if survey.created_at else None
        }

    def get_all_survey_stats(self) -> List[Dict[str, Any]]:
        """
        Retrieve statistics for all published surveys.

        Returns:
            List[dict]: A list of dictionaries containing survey stats.
        """
        surveys = self.session.query(Survey).filter(Survey.published==True)
        stats = []

        for survey in surveys:
            response_count = self.session.query(Response).filter(Response.survey_id == survey.id).count()
            question_count = self.session.query(Question).filter(Question.survey_id == survey.id).count()

            stats.append({
                "survey_id": survey.id,
                "title": survey.title,
                "total_responses": response_count,
                "total_questions": question_count,
                "created_at": survey.created_at.isoformat() if survey.created_at else None
            })

        return stats
    
    def create_survey_from_csv(self, file, title: str, description: str) -> Survey:
        """
        Parse a CSV file and create a new survey and its questions.

        Expects CSV columns: 'text', 'type', 'options', 'required', 'order'.
        The 'options' column (for choice-based questions) must be a valid Python list string (e.g., "['Yes', 'No']").

        Args:
            file (FileStorage): Uploaded CSV file containing question data.
            title (str): Title for the new survey.
            description (str): Description of the survey.

        Returns:
            Survey: The created Survey object.
        """
        survey_data = {"title": title, "description": description}
        survey = Survey(**survey_data)

        self.session.add(survey)
        self.session.flush()

        reader = csv.DictReader(TextIOWrapper(file, encoding='utf-8'))
        for row in reader:
            options = row.get('options')
            try:
                options = ast.literal_eval(options) if options else None
            except Exception:
                options = None

            question = Question(
                survey_id=survey.id,
                text=row.get('text', ''),
                type=row.get('type', 'text'),
                options=options,
                required=row.get('required', '').lower() == 'true',
                order=int(row.get('order', 0)) if row.get('order') else 0
            )
            self.session.add(question)

        self.session.commit()
        self.session.refresh(survey)
        return survey
