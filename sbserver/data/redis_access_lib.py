import json
import redis

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


def add_event(r, uuid, event: EventModel):
    r.set('event.uuid-event.details:' + uuid, json.dumps(event, default=vars))
    r.sadd('event.uuids', uuid)
    for x in event.tags:
        r.sadd(x, uuid)


def del_event(r, uuid):
    r.delete('event.uuid-event.details:' + uuid)
    r.srem('event.uuids', uuid)
    for tag in get_event(r, uuid)['tags']:
        r.srem('tag:' + tag)


def get_event(r, uuid):
    return json.loads(r.get('event.uuid-event.details:' + uuid))


def get_all_events(r):
    return [get_event(r, x) for x in r.smembers('event.uuids')]


def get_events_by_tag(r, tag):
    return r.smembers('tag:' + tag)
