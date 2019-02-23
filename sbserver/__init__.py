from flask import Flask, Blueprint
from flask_redis import FlaskRedis
from flask_restplus import Api

app = Flask(__name__)
app_routes = Blueprint('v1', __name__)
api = Api(app_routes, prefix='/v1')
red = FlaskRedis(app, decode_responses=True)

import sbserver.routes.events  # noqa

app.register_blueprint(app_routes)
