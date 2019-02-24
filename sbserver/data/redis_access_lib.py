import json
import redis


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


def add_event(r, uuid, event):
    r.set('event.uuid-event.details:' + uuid, json.dumps(event, default=lambda o: o.__dict__))
    add_event_to_set(r, uuid, event)


def del_event(r, uuid):
    r.delete('event.uuid-event.details:' + uuid)


def get_all_events(r):
    event_list = []
    for x in r.keys('*event*'):
        event_list.append(json.loads(r.get(x)))
    return event_list


def add_event_to_set(r, uuid, event):
    for x in event.tags:
        r.sadd(x, "event.uuid-event.details:" + uuid)


def get_events_by_tag(r, tag):
    return r.smembers(tag)
