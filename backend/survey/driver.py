from flask_cors import CORS
from flask_restful import Api

from survey.app import app
from survey.endpoints.ping_endpoint import PingEndpoint
from survey.endpoints.survey_endpoint import (
    ResponseAPI,
    SurveyAPI,
    SurveyStatsAPI,
    SurveyUploadAPI,
    ShareSurveyAPI,
)
from survey.utils.utils import get_logger

api = Api(app)

logger = get_logger()

# Register API resources
api.add_resource(PingEndpoint, "/survey/ping")
api.add_resource(SurveyAPI, 
    '/surveys',
    '/surveys/<int:survey_id>'
)
api.add_resource(SurveyUploadAPI, '/surveys/upload')
api.add_resource(ResponseAPI,
    '/surveys/<int:survey_id>/submit',
    '/responses/<int:response_id>'
)
api.add_resource(SurveyStatsAPI, '/surveys/<int:survey_id>/stats')
api.add_resource(ShareSurveyAPI, '/surveys/<int:survey_id>/share')

CORS(app)
api_enabled_app = app

if __name__ == "__main__":
    app.run(debug=True, port=5000)
