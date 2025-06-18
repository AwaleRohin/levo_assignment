from werkzeug.exceptions import HTTPException

class SurveyException(HTTPException):
    def __init__(self, message, status_code=400):
        super().__init__(description=message)
        self.code = status_code

class SurveyNotFoundError(SurveyException):
    def __init__(self, survey_id):
        super().__init__(f"Survey {survey_id} not found", 404)
