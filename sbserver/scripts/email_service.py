import time

import json
import re
import yaml
from bs4 import BeautifulSoup
from difflib import SequenceMatcher
from email_helper import EmailReceiver
from fitipy import Fitipy
from os.path import isfile
from prettyparse import create_parser

from sbserver.database import Event
from sbserver.relevancy import calc_freq, relevant_topics, get_keywords_uiuc
from sbserver.stateless_class import StatelessClass

usage = '''
    Run the Swing By email service
    
    :auth_file str
        Authentication yaml with username, password, and optionally pop3_host
    :-c --cache-file str .email-cache
        File prefix to store the most recent email id
'''


def main():
    args = create_parser(usage).parse_args()
    num_seen_file = Fitipy(args.cache_file + '.num')
    topics_cache = args.cache_file + '.topics.json'
    if not isfile(topics_cache):
        print('Generating topics...')
        with open(topics_cache, 'w') as f:
            json.dump(get_keywords_uiuc(), f)
    with open(topics_cache) as f:
        topics = json.load(f)

    num_seen = num_seen_file.read().read(0, int)
    with open(args.auth_file) as f:
        auth = yaml.load(f)
    email = auth['username']
    password = auth['password']
    server = auth.get('pop3_host', 'pop3.' + email.split('@')[-1])
    client = StatelessClass(
        EmailReceiver, email=email, password=password, server=server
    )  # type: EmailReceiver

    print('Waiting for emails...')
    while True:
        num_messages = len(client.get_list())
        if num_messages < num_seen:
            num_seen = num_messages
            num_seen_file.write().write(num_seen)
        if num_messages <= num_seen:
            time.sleep(1)
            continue
        for msg_id in range(num_seen + 1, num_messages + 1):
            email = client.get_email(msg_id)
            print('Found new email from {} titled {}.'.format(email['From'], email['Subject']))
            email_txt = '\n'.join(email['text'])
            email_txt = BeautifulSoup(email_txt).text
            email_txt = re.sub(r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))', '', email_txt)

            freq = calc_freq(email_txt, topics)
            tags = relevant_topics(freq)
            print('Found the following tags:', ', '.join(tags))
            events = Event.find()
            matched_events = [
                event for event in events
                if event.get('emailSrc') and
                   SequenceMatcher(a=event['emailSrc'], b=email_txt).ratio() > 0.9
            ]
            if matched_events:
                print('Ignoring, similar to {} other emails'.format(len(matched_events)))
            else:
                Event.add({
                    'name': email['Subject'],
                    'description': email_txt,
                    'location': '',
                    'time': int(time.time()),
                    'tags': tags,
                    'emailSrc': email_txt
                })
            num_seen += 1
            num_seen_file.write().write(num_seen, str)
