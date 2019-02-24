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
        red.set('user.email-user.password:' + email, password)
        return email

    @staticmethod
    def delete(email):
        red.delete('user.email-user.password:' + email)

    @staticmethod
    def get_pass(email):
        return red.get('user.email-user.password:' + email)


class Event:
    @staticmethod
    def add(event: dict):
        uuid = event['uuid'] = str(uuid4())
        tags = event.setdefault('tags', [])
        red.set('event.uuid-event.details:' + uuid, json.dumps(event))
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
