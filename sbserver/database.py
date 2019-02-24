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
class Event:
    uuid = RKey()
    data = RKey()

    model = api.model("event", {
        'name': fields.String(desription='Name of event', required=True),
        'description': fields.String(description='Description of event', required=True),
        'location': fields.String(description='Location of event', required=True),
        'time': fields.DateTime(description='UTC time string formatted as ISO 8601', required=True),
        'duration': fields.Float(description='Number of hours of event'),
        'timeStr': fields.String(description='String of time (ie. September 3rd at 4pm)'),
        'tags': fields.List(fields.String, description='Tags associated with event'),
        'uuid': fields.String(readonly=True, description='Generated uuid of object')
    })

    @staticmethod
    def add(event: dict):
        uuid = event['uuid'] = str(uuid4())
        tags = event.setdefault('tags', [])
        red.set(Event.uuid(uuid) & Event.data, json.dumps(event))
        red.sadd(Event.uuid, uuid)
        for tag in tags:
            red.sadd(Tag.name, tag)
            red.sadd(Tag.name(tag), uuid)
        return uuid

    @classmethod
    def delete(cls, uuid):
        tags = cls.get(uuid)['tags']
        red.delete(Event.uuid(uuid) & Event.data)
        red.srem(Event.uuid, uuid)
        for tag in tags:
            red.srem(Tag.name(tag), uuid)
            if red.scard(Tag.name(tag)) == 0:
                red.srem(Tag.name, tag)

    @staticmethod
    def exists(uuid):
        return red.sismember('event.uuids', uuid)

    @staticmethod
    def get(uuid):
        event = json.loads(red.get(Event.uuid(uuid) & Event.data))
        event['time'] = datetime.datetime.fromtimestamp(event['time'])
        return event

    @classmethod
    def get_all(cls):
        return [cls.get(x) for x in red.smembers(Event.uuid)]

    @classmethod
    def get_by_tag(cls, tag):
        return [cls.get(uuid) for uuid in red.smembers(Tag.name(tag))]
