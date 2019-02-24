import time

from flask import request
from flask_restplus import Resource
from flask_restplus.inputs import datetime_from_iso8601
from werkzeug.exceptions import NotFound

from sbserver import api
from sbserver.database import Event


@api.route('/event/<uuid>')
class EventInfoRoute(Resource):
    @api.marshal_with(Event.model)
    def get(self, uuid):
        return Event.get(uuid)

    def delete(self, uuid):
        if not Event.exists(uuid):
            raise NotFound('Uuid not found: ' + uuid)
        Event.delete(uuid)
        return {'status': 'success'}


@api.route('/events')
class EventCreateRoute(Resource):
    @api.marshal_list_with(Event.model)
    def get(self):
        tag = request.args.get('tag')
        return Event.find(tag)

    @api.expect(Event.model)
    @api.marshal_with(Event.model)
    def post(self):
        data = api.payload
        t = datetime_from_iso8601(data['time'])
        timestamp = int(time.mktime(t.timetuple()))
        data['time'] = timestamp
        uuid = Event.add(data)
        return Event.get(uuid)
