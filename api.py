from flask import Flask
import redis_access_lib as rd
import json
from uuid import uuid4

class event():
    def __init__(self, name, desc, locat, time, tags):
        self.name = name
        self.desc = desc
        self.locat = locat
        self.time = time
        self.tags = tags
        



r = rd.open_connection('localhost', 6379)
#value = rd.get_pass(r, "sally@gmail.com")
#rd.add_user(r, 'sally@gmail.com', '34567')
#print(value)
#Event = event('Git Semniar', 'Come learn about git!', 'Siebel', '2-25-19-24:00', ['computer science', 'version control'])
#rd.add_event(r, uuid4().hex, json.dumps(Event, default=lambda o: o.__dict__))
print(r.get(rd.get_all_events(r)[1]))