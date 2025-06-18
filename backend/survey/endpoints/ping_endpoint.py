from flask_restful import Resource


class PingEndpoint(Resource):
    def get(self):
        return {"status": "ok"}
