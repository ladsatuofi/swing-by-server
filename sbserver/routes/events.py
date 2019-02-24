from flask import request
from flask_restplus import Resource
from werkzeug.exceptions import BadRequest

from sbserver import api, red
from sbserver.data.model import EventModel
from sbserver.data.redis_access_lib import get_event, get_events_by_tag, get_all_events, add_event


@api.route('/event/<string:uuid>')
class EventInfoRoute(Resource):
    def get(self, uuid):
        return get_event(red, uuid)


@api.route('/event')
class EventCreateRoute(Resource):
    def get(self):
        tag = request.params.get('tag')
        return get_events_by_tag(red, tag) if tag else get_all_events(red)

    def post(self):
        data = request.get_json()
        try:
            event = EventModel(data['name'], data['description'], data['location'],
                               data['time'], data['tags'])
        except KeyError as e:
            raise BadRequest('Missing parameter: ' + str(e))

        uuid = add_event(red, event)
        return get_event(red, uuid)
