from functools import wraps


class StatelessClass:
    """Wraps a class so that each function call creates a new instance"""
    def __init__(self, cls, *args, **kwargs):
        self.cls = cls
        self.args = args
        self.kwargs = kwargs

    def __getattr__(self, attr):
        client = self.cls(*self.args, **self.kwargs)
        value = getattr(client, attr)
        if not callable(value):
            return value

        @wraps(value)
        def wrapped(*args, **kwargs):
            nonlocal client
            ret = value(*args, **kwargs)
            del client
            return ret

        return wrapped
