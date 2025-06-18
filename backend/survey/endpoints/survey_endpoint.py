import csv
import ast
from io import TextIOWrapper
from flask import request, jsonify
from werkzeug.exceptions import BadRequest, NotFound
from flask_restful import Resource
from sqlalchemy.orm import joinedload
from marshmallow import ValidationError

from survey.app import Session
from survey.models.models import Survey, Question, Response
from survey.models.models import (
    survey_schema, response_schema
)
from survey.services.survey_service import SurveyService


class SurveyAPI(Resource):
    def post(self):
        """Create a new survey with optional nested questions"""
        try:
            data = request.get_json()
            questions_data = data.pop("questions", [])

            with Session() as session:
                survey_service = SurveyService(session)
                survey = survey_service.create_survey(data, questions_data)
                return survey_schema.dump(survey), 201

        except ValidationError as e:
            raise BadRequest(e.messages)
        except Exception as e:
            raise BadRequest(str(e))

    def get(self, survey_id=None):
        """Get a survey (with questions) or list of surveys"""
        with Session() as session:
            survey_service = SurveyService(session)
            
            if survey_id:
                survey = survey_service.get_survey(survey_id)
                return survey_schema.dump(survey), 200

            # Get all surveys
            surveys = survey_service.get_all_surveys()
            return survey_schema.dump(surveys, many=True), 200

    def put(self, survey_id):
        """Update survey + replace questions"""
        try:
            data = request.get_json()
            questions_data = data.pop("questions", [])

            with Session() as session:
                survey_service = SurveyService(session)
                survey = survey_service.update_survey(survey_id, data, questions_data)
                return survey_schema.dump(survey), 200

        except ValidationError as e:
            raise BadRequest(e.messages)
        except Exception as e:
            raise BadRequest(str(e))

    def delete(self, survey_id):
        """Delete survey and cascade questions + responses"""
        with Session() as session:
            survey_service = SurveyService(session)
            survey_service.delete_survey(survey_id)
            return {"message": f"Survey {survey_id} deleted"}, 200


class SurveyUploadAPI(Resource):
    def post(self):
        """Create survey from CSV upload"""
        file = request.files.get('file')
        title = request.form.get("title", "Untitled Survey")
        description = request.form.get("description", "Untitled Survey")

        try:
            # Create survey
            survey = survey_schema.load({"title": title, "description": description})
            with Session() as session:
                session.add(survey)
                session.flush()

                # Process CSV rows into questions
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
                    session.add(question)

                session.commit()
                session.refresh(survey)
                return survey_schema.dump(survey), 201

        except ValidationError as e:
            raise BadRequest(e.messages)
        except Exception as e:
            raise BadRequest(f"Error creating survey: {str(e)}")

    def has_access(self, survey_id):
        return True


class ResponseAPI(Resource):
    def post(self, survey_id):
        """Create a new response for a survey"""
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
            raise BadRequest(e.messages)
        except Exception as e:
            raise BadRequest(f"Error creating response: {str(e)}")

    def get(self, survey_id=None, response_id=None):
        """Get all responses for a survey or a specific response"""
        with Session() as session:
            if response_id:
                response = session.query(Response).get(response_id)
                if not response:
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
                return response_schema.dump(responses, many=True)

    def put(self, response_id):
        """Update an existing response"""
        try:
            data = request.get_json()
            with Session() as session:
                response = session.query(Response).get(response_id)
                if not response:
                    raise NotFound(f"Response {response_id} not found")

                for field in ['answers', 'respondent_email']:
                    if field in data:
                        setattr(response, field, data[field])

                session.commit()
                return response_schema.dump(response)

        except ValidationError as e:
            raise BadRequest(e.messages)
        except Exception as e:
            raise BadRequest(f"Error updating response: {str(e)}")

    def delete(self, response_id):
        """Delete a response"""
        with Session() as session:
            response = session.query(Response).get(response_id)
            if not response:
                raise NotFound(f"Response {response_id} not found")

            session.delete(response)
            session.commit()
            return {"message": f"Response {response_id} deleted"}, 200


class SurveyStatsAPI(Resource):
    """New API for survey statistics"""
    def get(self, survey_id):
        """Get survey statistics"""
        with Session() as session:
            survey_service = SurveyService(session)
            stats = survey_service.get_survey_stats(survey_id)
            return stats
