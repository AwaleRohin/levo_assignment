from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from survey.models.models import Survey, Question, Response
from survey.utils.exceptions import SurveyNotFoundError


class SurveyService:
    def __init__(self, session: Session):
        self.session = session

    def create_survey(self, data: Dict[str, Any], questions_data: List[Dict[str, Any]]) -> Survey:
        """Create a new survey with questions"""
        
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
        return survey

    def get_survey(self, survey_id: int) -> Survey:
        """Get a survey by ID"""
        survey = self.session.query(Survey).filter(Survey.id == survey_id).first()
        if not survey:
            print("survey not found")
            raise SurveyNotFoundError(survey_id)
        return survey

    def get_all_surveys(self) -> List[Survey]:
        """Get all surveys"""
        return self.session.query(Survey).all()

    def update_survey(self, survey_id: int, data: Dict[str, Any], questions_data: List[Dict[str, Any]]) -> Survey:
        """Update a survey and its questions"""
        survey = self.get_survey(survey_id)
        
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
        """Delete a survey and all related data"""
        survey = self.get_survey(survey_id)
        
        # Delete related questions and responses
        self.session.query(Question).filter(Question.survey_id == survey.id).delete()
        self.session.query(Response).filter(Response.survey_id == survey.id).delete()
        
        self.session.delete(survey)
        self.session.commit()

    def get_survey_stats(self, survey_id: int) -> Dict[str, Any]:
        """Get statistics for a survey"""
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
