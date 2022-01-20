from flask import jsonify


class HealthCheckController:
    def ping(self):
        return jsonify({"ping": "pong"})
