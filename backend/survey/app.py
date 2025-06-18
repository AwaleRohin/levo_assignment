from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_marshmallow import Marshmallow
from sqlalchemy.orm import sessionmaker

from survey.utils.secrets_util import get_db_url
from survey.utils.exceptions import SurveyException

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = get_db_url()

db = SQLAlchemy(app)

ma = Marshmallow(app)

Session = None

def init_session():
    global Session
    Session = sessionmaker(bind=db.engine)

with app.app_context():
    init_session()

migrate = Migrate(app, db)

@app.errorhandler(SurveyException)
def handle_survey_exception(error):
    response = jsonify({
        'status': 'error',
        'message': error.description
    })
    response.status_code = error.code if hasattr(error, 'code') else 400
    return response