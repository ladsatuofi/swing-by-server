from prettyparse import create_parser

from sbserver import app

usage = '''
    Start debug backend server
    
    :-b --bind str 0.0.0.0
        Host to bind to
    :-p --port int 8000
        Port to bind to
'''


def main():
    args = create_parser(usage).parse_args()
    app.run(host=args.bind, port=int(args.port))
