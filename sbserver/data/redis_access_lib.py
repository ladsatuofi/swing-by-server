import datetime
import json
import redis
from uuid import uuid4


def open_connection(hostname, port):
    return redis.Redis(
        host=hostname,
        port=port,
        decode_responses=True)


def get_pass(r, email):
    return r.get('user.email-user.password:' + email)


def add_user(r, email, password):
    r.set('user.email-user.password:' + email, password)


def del_user(r, email):
    r.delete('user.email-user.password:' + email)


def add_event(r, name: str, description: str, location: str, time: int, time_str: str, tags: list,
              uuid=''):
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


def del_event(r, uuid):
    tags = get_event(r, uuid)['tags']
    r.delete('event.uuid-event.details:' + uuid)
    r.srem('event.uuids', uuid)
    for tag in tags:
        r.srem('tag:' + tag, uuid)


def is_event(r, uuid):
    return r.sismember('event.uuids', uuid)


def get_event(r, uuid):
    event = json.loads(r.get('event.uuid-event.details:' + uuid))
    event['time'] = datetime.datetime.fromtimestamp(event['time'])
    return event


def get_all_events(r):
    return [get_event(r, x) for x in r.smembers('event.uuids')]


def get_events_by_tag(r, tag):
    return [get_event(r, uuid) for uuid in r.smembers('tag:' + tag)]
