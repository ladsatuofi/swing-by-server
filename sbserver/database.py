import datetime
import json
import redis
from uuid import uuid4


def open_connection(hostname, port):
    return redis.Redis(
        host=hostname,
        port=port,
        decode_responses=True)


class User:
    @staticmethod
    def add(r, email, password):
        r.set('user.email-user.password:' + email, password)
        return email

    @staticmethod
    def delete(r, email):
        r.delete('user.email-user.password:' + email)

    @staticmethod
    def get_pass(r, email):
        return r.get('user.email-user.password:' + email)


class Event:
    @staticmethod
    def add(r, name: str, description: str, location: str,
            time: int, time_str: str, tags: list, uuid=''):
        uuid = uuid or str(uuid4())
        r.set('event.uuid-event.details:' + uuid, json.dumps({
            'name': name,
            'description': description,
            'location': location,
            'time': time,
            'timeStr': time_str,
            'tags': tags,
            'uuid': uuid
        }))
        r.sadd('event.uuids', uuid)
        for x in tags:
            r.sadd(x, uuid)
        return uuid

    @classmethod
    def delete(cls, r, uuid):
        tags = cls.get(r, uuid)['tags']
        r.delete('event.uuid-event.details:' + uuid)
        r.srem('event.uuids', uuid)
        for tag in tags:
            r.srem('tag:' + tag, uuid)

    @staticmethod
    def exists(r, uuid):
        return r.sismember('event.uuids', uuid)

    @staticmethod
    def get(r, uuid):
        event = json.loads(r.get('event.uuid-event.details:' + uuid))
        event['time'] = datetime.datetime.fromtimestamp(event['time'])
        return event

    @classmethod
    def get_all(cls, r):
        return [cls.get(r, x) for x in r.smembers('event.uuids')]

    @classmethod
    def get_by_tag(cls, r, tag):
        return [cls.get(r, uuid) for uuid in r.smembers('tag:' + tag)]
