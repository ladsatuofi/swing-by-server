import time
from flask import request
from flask_restplus import Resource, fields
from flask_restplus.inputs import datetime_from_iso8601
from werkzeug.exceptions import BadRequest, NotFound

from sbserver import api, red
from sbserver.data.model import EventModel
from sbserver.data.redis_access_lib import get_event, get_events_by_tag, get_all_events, add_event, del_event, is_event


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
        return get_event(red, uuid)

    def delete(self, uuid):
        if not is_event(red, uuid):
            raise NotFound('Uuid not found: ' + uuid)
        del_event(red, uuid)
        return {'status': 'success'}


@api.route('/events')
class EventCreateRoute(Resource):
    @api.marshal_list_with(EventApiModel)
    def get(self):
        tag = request.args.get('tag')
        return get_events_by_tag(red, tag) if tag else get_all_events(red)

    @api.expect(EventApiModel)
    @api.marshal_with(EventApiModel)
    def post(self):
        data = api.payload
        print(data)
        print(type(data), type(data.get('time')))
        event = EventModel(data['name'], data['description'], data['location'],
                               int(time.mktime(datetime_from_iso8601(data['time']).timetuple())), data.get('timeStr', ''), data.get('tags', []))

        uuid = add_event(red, event)
        return get_event(red, uuid)
