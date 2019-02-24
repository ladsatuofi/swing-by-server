import time

from flask import request
from flask_restplus import Resource, fields
from flask_restplus.inputs import datetime_from_iso8601
from werkzeug.exceptions import NotFound

from sbserver import api, red
from sbserver.database import Event

EventApiModel = api.model("event", {
    'name': fields.String(desription='Name of event', required=True),
    'description': fields.String(description='Description of event', required=True),
    'location': fields.String(description='Location of event', required=True),
    'time': fields.DateTime(description='UTC time string formatted as ISO 8601', required=True),
    'timeStr': fields.String(description='String of time (ie. September 3rd at 4pm)'),
    'tags': fields.List(fields.String, description='Tags associated with event'),
    'uuid': fields.String(readonly=True, description='Generated uuid of object')
})


@api.route('/event/<uuid>')
class EventInfoRoute(Resource):
    @api.marshal_with(EventApiModel)
    def get(self, uuid):
        return Event.get(red, uuid)

    def delete(self, uuid):
        if not Event.exists(red, uuid):
            raise NotFound('Uuid not found: ' + uuid)
        Event.delete(red, uuid)
        return {'status': 'success'}


@api.route('/events')
class EventCreateRoute(Resource):
    @api.marshal_list_with(EventApiModel)
    def get(self):
        tag = request.args.get('tag')
        return Event.get_by_tag(red, tag) if tag else Event.get_all(red)

    @api.expect(EventApiModel)
    @api.marshal_with(EventApiModel)
    def post(self):
        data = api.payload
        t = datetime_from_iso8601(data['time'])
        timestamp = int(time.mktime(t.timetuple()))
        uuid = Event.add(red, data['name'], data['description'], data['location'],
                         timestamp, data.get('timeStr', ''), data.get('tags', []))
        return Event.get(red, uuid)
