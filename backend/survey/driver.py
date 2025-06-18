from flask_cors import CORS
from flask_restful import Api

from survey.app import app
from survey.utils.utils import get_logger
from survey.endpoints.ping_endpoint import PingEndpoint

api = Api(app)

logger = get_logger()

api.add_resource(PingEndpoint, "/ping")
    

CORS(app)
api_enabled_app = app

if __name__ == "__main__":
    app.run(debug=True, port=5000)
