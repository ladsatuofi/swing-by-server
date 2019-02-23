from flask import Flask
import sbserver.data.redis_access_lib as rd
from uuid import uuid4
from sbserver.data import model


r = rd.open_connection('localhost', 6379)
#value = rd.get_pass(r, "sally@gmail.com")
#rd.add_user(r, 'sally@gmail.com', '34567')
#print(value)
#Event = model.event('Learn to code', 'Learn code at Siebel!', 'Siebel', '2-29-19-23:10', ['computer-science', 'programming'])
#rd.add_event(r, uuid4().hex, Event)
#print(rd.get_events_by_tag(r,'computer-science'))
print(rd.get_all_events(r))
#rd.add_event(r, uuid4().hex, json.dumps(Event, default=lambda o: o.__dict__))
#print(rd.get_all_events(r))
#event = json.loads(r.get(rd.get_all_events(r)[0]))
#event = rd.get_all_events(r)
#print(event)
#r.delete(event[0])
#print(event['tags'][0])
#rd.add_to_set(r)
