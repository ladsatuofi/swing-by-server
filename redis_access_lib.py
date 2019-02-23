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

def add_event(r, uuid, event):
    r.set('event.uuid-event.details:' + uuid, event)

def get_all_events(r):
    return r.keys('*event*')