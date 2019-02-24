import json
import redis
import datetime
from uuid import uuid4

from sbserver.data.model import EventModel


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


def add_event(r, event: EventModel):
    event.uuid = uuid = event.uuid or str(uuid4())
    r.set('event.uuid-event.details:' + uuid, json.dumps(event, default=vars))
    r.sadd('event.uuids', uuid)
    for x in event.tags:
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
