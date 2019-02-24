import time

import yaml
from email_helper import EmailReceiver
from fitipy import Fitipy
from prettyparse import create_parser

from sbserver.stateless_class import StatelessClass

usage = '''
    Run the Swing By email service
    
    :auth_file str
        Authentication yaml with username, password, and optionally pop3_host
    :-c --cache-file str .email-cache
        File to store the most recent email id
'''


def main():
    args = create_parser(usage).parse_args()
    num_seen_file = Fitipy(args.cache_file)
    num_seen = num_seen_file.read().read(0, int)
    with open(args.auth_file) as f:
        auth = yaml.load(f)
    email = auth['username']
    password = auth['password']
    server = auth.get('pop3_host', 'pop3.' + email.split('@')[-1])
    client = StatelessClass(
        EmailReceiver, email=email, password=password, server=server
    )  # type: EmailReceiver

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
            num_seen += 1
            num_seen_file.write().write(num_seen, str)
