import datetime
import json
import redis
from uuid import uuid4

from sbserver import red


def open_connection(hostname, port):
    return redis.Redis(
        host=hostname,
        port=port,
        decode_responses=True)


class User:
    @staticmethod
    def add(email, password):
        red.set('usered.email-usered.password:' + email, password)
        return email

    @staticmethod
    def delete(email):
        red.delete('usered.email-usered.password:' + email)

    @staticmethod
    def get_pass(email):
        return red.get('usered.email-usered.password:' + email)


class Event:
    @staticmethod
    def add(name: str, description: str, location: str,
            time: int, time_str: str, tags: list, uuid=''):
        uuid = uuid or str(uuid4())
        red.set('event.uuid-event.details:' + uuid, json.dumps({
            'name': name,
            'description': description,
            'location': location,
            'time': time,
            'timeStr': time_str,
            'tags': tags,
            'uuid': uuid
        }))
        red.sadd('event.uuids', uuid)
        for x in tags:
            red.sadd(x, uuid)
        return uuid

    @classmethod
    def delete(cls, uuid):
        tags = cls.get(uuid)['tags']
        red.delete('event.uuid-event.details:' + uuid)
        red.srem('event.uuids', uuid)
        for tag in tags:
            red.srem('tag:' + tag, uuid)

    @staticmethod
    def exists(uuid):
        return red.sismember('event.uuids', uuid)

    @staticmethod
    def get(uuid):
        event = json.loads(red.get('event.uuid-event.details:' + uuid))
        event['time'] = datetime.datetime.fromtimestamp(event['time'])
        return event

    @classmethod
    def get_all(cls):
        return [cls.get(x) for x in red.smembers('event.uuids')]

    @classmethod
    def get_by_tag(cls, tag):
        return [cls.get(uuid) for uuid in red.smembers('tag:' + tag)]
