import os
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_marshmallow import Marshmallow
from sqlalchemy.orm import sessionmaker
from flask_mail import Mail

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


app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.mailersend.net')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'true').lower() == 'true'
app.config['MAIL_USE_SSL'] = os.getenv('MAIL_USE_SSL', 'false').lower() == 'true'
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER')

mail = Mail(app)

@app.errorhandler(SurveyException)
def handle_survey_exception(error):
    response = jsonify({
        'status': 'error',
        'message': error.description
    })
    response.status_code = error.code if hasattr(error, 'code') else 400
    return response