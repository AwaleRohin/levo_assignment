from datetime import datetime
from survey.app import db, ma


class Survey(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    questions = db.relationship('Question', backref='survey', cascade='all, delete-orphan')
    published = db.Column(db.Boolean(), default=True)
    created_at = db.Column(db.DateTime, default=datetime.now())


class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    survey_id = db.Column(db.Integer, db.ForeignKey('survey.id'), nullable=False)
    text = db.Column(db.String(500), nullable=False)
    type = db.Column(db.String(50), nullable=False)
    options = db.Column(db.JSON, nullable=True)
    required = db.Column(db.Boolean, default=False)
    order = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.now())


class Response(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    survey_id = db.Column(db.Integer, db.ForeignKey('survey.id'), nullable=False)
    answers = db.Column(db.JSON, nullable=False)
    respondent_email = db.Column(db.String(200),nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now())


class SurveySchema(ma.SQLAlchemyAutoSchema):
    questions = ma.Nested("QuestionSchema", many=True)
    class Meta:
        model = Survey
        include_fk = True
        include_relationships = True
        load_instance = True


class QuestionSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Question
        include_fk = True
        include_relationships = True
        load_instance = True


class ResponseSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Response
        include_fk = True
        include_relationships = True
        load_instance = True


survey_schema = SurveySchema()
surveys_schema = SurveySchema(many=True)
question_schema = QuestionSchema()
questions_schema = QuestionSchema(many=True)
response_schema = ResponseSchema()
responses_schema = ResponseSchema(many=True)
