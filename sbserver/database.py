import datetime
import json
import redis
from flask_restplus import fields
from uuid import uuid4

from sbserver import red, api
from sbserver.redi import RClass, RKey


def open_connection(hostname, port):
    return redis.Redis(
        host=hostname,
        port=port,
        decode_responses=True)


@RClass()
class User:
    uuid = RKey()
    email = RKey()
    password = RKey()
    karma = RKey()
    data = RKey()

    @staticmethod
    def add(email, password):
        uuid = str(uuid4())
        red.set(User.email(email) & User.password, password)
        red.set(User.uuid(uuid) & User.data, json.dumps({
            'email': email,
            'uuid': uuid
        }))
        red.sadd(User.uuid, uuid)
        return uuid

    @staticmethod
    def get(uuid):
        return json.loads(red.get(User.uuid(uuid) & User.data))

    @classmethod
    def delete(cls, uuid):
        email = cls.get(uuid)['email']
        red.delete(User.email(email) & User.password)
        red.delete(User.uuid(uuid) & User.data)
        red.delete(User.uuid(uuid) & User.karma)
        red.srem(User.uuid, uuid)

    @staticmethod
    def get_pass(email):
        return red.get(User.email(email) & User.password)


@RClass()
class Tag:
    name = RKey()


@RClass()
class EventState:
    pending = RKey()
    valid = RKey()
    invalid = RKey()

    name = RKey()  # key label


@RClass()
class Event:
    uuid = RKey()
    data = RKey()
    upvotes = RKey()  # list of user uuids
    upvotes_set = RKey()  # set of user uuids
    views = RKey()  # set of user uuids
    state = RKey()  # One of EventState strings

    model = api.model("event", {
        'name': fields.String(desription='Name of event', required=True),
        'description': fields.String(description='Description of event', required=True),
        'location': fields.String(description='Location of event', required=True),
        'time': fields.DateTime(description='UTC time string formatted as ISO 8601', required=True),
        'duration': fields.Float(description='Number of hours of event'),
        'timeStr': fields.String(description='String of time (ie. September 3rd at 4pm)'),
        'tags': fields.List(fields.String, description='Tags associated with event'),
        'uuid': fields.String(readonly=True, description='Generated uuid of object'),
        'state': fields.String(readonly=True, description='One of: EventState.pending, '
                                                          'EventState.valid, EventState.invalid'),
        'emailSrc': fields.String(readonly=True, description='Raw source email if forwarded')
    })

    @staticmethod
    def add(event: dict) -> str:
        uuid = event['uuid'] = str(uuid4())
        tags = event.setdefault('tags', [])
        state = event.setdefault('state', EventState.pending)
        red.set(Event.uuid(uuid) & Event.data, json.dumps(event))
        red.sadd(EventState.name(state), uuid)
        red.sadd(Event.uuid, uuid)
        for tag in tags:
            red.sadd(Tag.name, tag)
            red.sadd(Tag.name(tag), uuid)
        return uuid

    @classmethod
    def delete(cls, uuid):
        data = cls.get(uuid)
        red.delete(Event.uuid(uuid) & Event.data)
        red.delete(Event.uuid(uuid) & Event.upvotes)
        red.delete(Event.uuid(uuid) & Event.upvotes_set)
        red.delete(Event.uuid(uuid) & Event.views)
        red.srem(EventState.name(data['state']), uuid)
        red.srem(Event.uuid, uuid)
        for tag in data['tags']:
            red.srem(Tag.name(tag), uuid)
            if red.scard(Tag.name(tag)) == 0:
                red.srem(Tag.name, tag)

    @classmethod
    def set_state(cls, uuid, state):
        data = cls.get(uuid)
        red.srem(EventState.name(data['state']), uuid)
        data['state'] = state
        red.sadd(EventState.name(state), uuid)
        red.set(Event.uuid(uuid) & Event.data, json.dumps(data))

    @staticmethod
    def mark_as_viewed(uuid, user_uuid) -> bool:
        return bool(red.sadd(Event.uuid(uuid) & Event.views, user_uuid))

    @staticmethod
    def mark_as_upvoted(uuid, user_uuid) -> bool:
        if red.sadd(Event.upvotes_set, user_uuid):
            red.lpush(Event.uuid(uuid) & Event.views, user_uuid)
            return True
        return False

    @staticmethod
    def get_upvotes(uuid) -> list:
        return red.lrange(Event.uuid(uuid) & Event.upvotes, 0, -1)

    @staticmethod
    def get_views(uuid) -> list:
        return red.smembers(Event.uuid(uuid) & Event.views)

    @staticmethod
    def exists(uuid) -> bool:
        return red.sismember(Event.uuid, uuid)

    @staticmethod
    def get(uuid) -> dict:
        event = json.loads(red.get(Event.uuid(uuid) & Event.data))
        event['time'] = datetime.datetime.fromtimestamp(event['time'])
        return event

    @classmethod
    def find(cls, tag=None, event_state=None) -> list:
        uuids = set(red.smembers(Event.uuid))
        if tag:
            uuids &= set(red.smembers(Tag.name(tag)))
        if event_state:
            uuids &= set(red.smembers(EventState.name(event_state)))
        return [cls.get(x) for x in uuids]
