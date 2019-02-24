class RKey:
    """
    Key for use in composing redis addresses
    """

    def __init__(self, name='', target=''):
        self.name = name
        self.target = target

    def __str__(self):
        return self.name + bool(self.target) * ':' + self.target

    def __call__(self, target):
        duplicate = RKey(self.name, self.target)
        duplicate.target = str(target)
        return duplicate

    def __and__(self, other):
        if not isinstance(other, (RKey, str)):
            raise ValueError("Can only & between RKey and RKey/str/int")
        if isinstance(other, str):
            other = RKey(other)
        if other.target:
            raise ValueError("Only left RKey should have parameter")
        return RKey(self.name + '-' + other.name, self.target)


def RClass():
    def decorator(cls):
        class_name = cls.__name__
        for name, obj in vars(cls).items():
            if isinstance(obj, RKey):
                obj.name = class_name + '.' + name
        return cls

    return decorator
