import csv
import ast
from io import TextIOWrapper
from typing import Optional, List, Any, Dict

from flask import request, jsonify
from werkzeug.datastructures import FileStorage
from werkzeug.exceptions import BadRequest, NotFound
from flask_restful import Resource
from sqlalchemy.orm import joinedload
from marshmallow import ValidationError

from survey.app import Session
from survey.tasks.email_tasks import send_email_task
from survey.models.models import Survey, Question, Response
from survey.models.models import (
    survey_schema, response_schema
)
from survey.services.survey_service import SurveyService
from survey.utils.utils import get_logger

logger = get_logger()


class SurveyAPI(Resource):
    """API for creating, retrieving, updating, and deleting surveys."""
    def post(self) -> tuple[dict, int]:
        """
        Create a new survey with optional nested questions.

        Returns:
            tuple: JSON representation of the created survey and HTTP status code 201.

        Raises:
            BadRequest: If validation fails or an exception occurs.
        """
        try:
            data: dict = request.get_json(force=True)
            questions_data: List[Dict[str, Any]] = data.pop("questions", [])

            with Session() as session:
                survey_service = SurveyService(session)
                survey = survey_service.create_survey(data, questions_data)
                return survey_schema.dump(survey), 201

        except ValidationError as e:
            logger.error("Validation Error while creating Survey.")
            raise BadRequest(e.messages)
        except Exception as e:
            logger.error(f"Exception while creating Survey. {str(e)}")
            raise BadRequest(str(e))

    def get(self, survey_id: Optional[int] = None) -> tuple[Any, int]:
        """
        Retrieve a specific survey (with questions) or a list of all surveys.

        Args:
            survey_id (int, optional): ID of the survey to retrieve.

        Returns:
            tuple: JSON representation of the survey(s) and HTTP status code 200.
        """
        with Session() as session:
            survey_service = SurveyService(session)
            
            if survey_id:
                survey = survey_service.get_survey(survey_id)
                return survey_schema.dump(survey), 200

            # Get all surveys
            surveys = survey_service.get_all_surveys()
            return survey_schema.dump(surveys, many=True), 200

    def put(self, survey_id: int) -> tuple[dict, int]:
        """
        Update an existing survey and its questions.

        Args:
            survey_id (int): ID of the survey to update.

        Returns:
            tuple: JSON representation of the updated survey and HTTP status code 200.

        Raises:
            BadRequest: If validation fails or an exception occurs.
        """
        try:
            data = request.get_json()
            questions_data = data.pop("questions", [])

            with Session() as session:
                survey_service = SurveyService(session)
                survey = survey_service.update_survey(survey_id, data, questions_data)
                return survey_schema.dump(survey), 200

        except ValidationError as e:
            logger.error("Validation Error while updating Survey.")
            raise BadRequest(e.messages)
        except Exception as e:
            logger.error(f"Exception while updating Survey for id: {survey_id}. {str(e)}")
            raise BadRequest(str(e))

    def delete(self, survey_id: int) -> tuple[dict, int]:
        """
        Delete a survey and cascade delete its questions and responses.

        Args:
            survey_id (int): ID of the survey to delete.

        Returns:
            tuple: A confirmation message and HTTP status code 200.
        """
        with Session() as session:
            survey_service = SurveyService(session)
            survey_service.delete_survey(survey_id)
            logger.info(f"Deleted Survey for id: {survey_id}.")
            return {"message": f"Survey {survey_id} deleted"}, 200


class SurveyUploadAPI(Resource):
    """API for uploading a survey via a CSV file."""
    def post(self) -> tuple[dict, int]:
        """
        Create a new survey from an uploaded CSV file.

        Expects:
            - `csv` (file): CSV file with survey questions.
            - `title` (form field, optional): Survey title.
            - `description` (form field, optional): Survey description.

        Returns:
            tuple: JSON representation of the created survey and HTTP status code 201.

        Raises:
            BadRequest: If file is missing, not a CSV, too large, or data is invalid.
        """
        file: Optional[FileStorage] = request.files.get("csv")
        title: str = request.form.get("title", "Untitled Survey")
        description: str = request.form.get("description", "Untitled Survey")

        if not file or file.mimetype != "text/csv":
            logger.error("Uploaded file must be a valid CSV.")
            raise BadRequest("Uploaded file must be a valid CSV.")

        MAX_FILE_SIZE_MB = 2
        MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

        file.seek(0, 2)
        file_size = file.tell()
        file.seek(0)

        if file_size > MAX_FILE_SIZE_BYTES:
            raise BadRequest(f"CSV file size exceeds {MAX_FILE_SIZE_MB}MB limit.")

        try:
            with Session() as session:
                survey_service = SurveyService(session)
                survey = survey_service.create_survey_from_csv(file, title, description)
                return survey_schema.dump(survey), 201

        except ValidationError as e:
            logger.error("Validation error during survey CSV upload.")
            raise BadRequest(e.messages)
        except Exception as e:
            logger.error(f"Error during survey CSV upload: {str(e)}")
            raise BadRequest(f"Error creating survey: {str(e)}")


class ResponseAPI(Resource):
    """API for managing responses to surveys."""
    def post(self, survey_id) -> tuple[dict, int]:
        """
        Submit a new response for a given survey.

        Args:
            survey_id (int): ID of the survey being answered.

        Returns:
            tuple: JSON representation of the created response and HTTP status code 201.

        Raises:
            NotFound: If the survey is not found.
            BadRequest: If validation fails or another error occurs.
        """
        try:
            data = request.get_json()
            with Session() as session:
                # Validate survey exists
                survey = session.query(Survey).filter(Survey.id == survey_id).first()
                if not survey:
                    raise NotFound(f"Survey {survey_id} not found")

                response = response_schema.load(data)
                response.survey_id = survey_id
                session.add(response)
                session.commit()
                return response_schema.dump(response), 201

        except ValidationError as e:
            logger.error("Validation Error while adding Response.")
            raise BadRequest(e.messages)
        except Exception as e:
            logger.error(f"Exception while creating Response. {str(e)}")
            raise BadRequest(f"Error creating response: {str(e)}")

    def get(self, survey_id: Optional[int] = None, response_id: Optional[int] = None) -> tuple[Any, int]:
        """
        Retrieve responses. If `response_id` is provided, return specific response.
        If only `survey_id` is given, return all responses for that survey.
        If neither is given, return all responses.

        Args:
            survey_id (int, optional): ID of the survey.
            response_id (int, optional): ID of the specific response.

        Returns:
            tuple: JSON list of responses or single response and HTTP status code.
        """
        with Session() as session:
            if response_id:
                response = session.query(Response).get(response_id)
                if not response:
                    logger.error(f"Response {response_id} not found")
                    raise NotFound(f"Response {response_id} not found")
                return response_schema.dump(response)
            elif survey_id:
                responses = (
                    session.query(Response)
                    .filter(Response.survey_id == survey_id)
                    .all()
                )
                return response_schema.dump(responses, many=True)
            else:
                responses = session.query(Response).all()
                return response_schema.dump(responses, many=True), 200

    def put(self, response_id: int) -> tuple[dict, int]:    
        """
        Update an existing survey response.

        Args:
            response_id (int): ID of the response to update.

        Returns:
            tuple: JSON representation of the updated response and HTTP status code 200.

        Raises:
            NotFound: If the response is not found.
            BadRequest: If the update fails.
        """
        try:
            data = request.get_json()
            with Session() as session:
                response = session.query(Response).get(response_id)
                if not response:
                    logger.error(f"Response {response_id} not found")
                    raise NotFound(f"Response {response_id} not found")

                for field in ['answers']:
                    if field in data:
                        setattr(response, field, data[field])

                session.commit()
                return response_schema.dump(response), 200

        except ValidationError as e:
            raise BadRequest(e.messages)
        except Exception as e:
            raise BadRequest(f"Error updating response: {str(e)}")

    def delete(self, response_id) -> tuple[dict, int]:
        """
        Delete a response by ID.

        Args:
            response_id (int): ID of the response to delete.

        Returns:
            tuple: Confirmation message and HTTP status code 200.

        Raises:
            NotFound: If the response is not found.
        """
        with Session() as session:
            response = session.query(Response).get(response_id)
            if not response:
                logger.error(f"Response {response_id} not found")
                raise NotFound(f"Response {response_id} not found")

            session.delete(response)
            session.commit()
            logger.debug("Response {response_id} deleted")
            return {"message": f"Response {response_id} deleted"}, 200


class SurveyStatsAPI(Resource):
    """API for retrieving statistics about surveys."""
    def get(self, survey_id: Optional[int] = None) -> tuple[Any, int]:
        """
        Retrieve statistics for a specific survey or for all surveys.

        Args:
            survey_id (int, optional): ID of the survey to get stats for.

        Returns:
            tuple: Survey statistics and HTTP status code 200.
        """
        with Session() as session:
            survey_service = SurveyService(session)
            if survey_id:
                stats = survey_service.get_survey_stats(survey_id)
            else:
                stats = survey_service.get_all_survey_stats()
            return stats, 200


class ShareSurveyAPI(Resource):
    """API for sharing a survey via email."""
    def post(self, survey_id: int) -> tuple[dict, int]:
        """
        Send the survey link to one or more email addresses.

        Args:
            survey_id (int): ID of the survey to share.

        Returns:
            tuple: Confirmation message and HTTP status code 200 or 500 if email fails.

        Raises:
            BadRequest: If required fields are missing.
        """
        data: dict = request.get_json(force=True)
        emails: Optional[str] = data.get("emails")
        survey_link: Optional[str] = data.get("survey_link")

        if not emails or not survey_link:
            logger.warning("Missing 'emails' in request payload.")
            return {"error": "Missing required fields"}, 400

        try:
            result = send_email_task.delay(
                subject="You're Invited to Take a Survey",
                recipients=emails,
                body=f"Hi there!\n\nPlease complete the survey at:\n{survey_link}",
                html=f"<p>Please take the survey <a href='{survey_link}'>here</a>.</p>"
            )
            logger.info(f"Email send result: {result}")
            return {"message": "Survey email(s) sent!"}, 200
        except Exception as e:
            logger.error(f"Error sending email: {str(e)}")
            return {"error": f"Failed to send email: {str(e)}"}, 500
