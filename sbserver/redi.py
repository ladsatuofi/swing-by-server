class RKey(str):
    """
    Key for use in composing redis addresses
    """

    def __init__(self, name='', target=''):
        super().__init__()

    @property
    def name(self):
        return self.split(':')[0]

    @property
    def target(self):
        return self.split(':')[-1] if ':' in self else ''

    def __str__(self):
        return self.name + bool(self.target) * ':' + self.target

    def __call__(self, target):
        print(self.name, self.target)
        duplicate = RKey(self.name + ':' + target)
        print(duplicate)
        return duplicate

    def __and__(self, other):
        if not isinstance(other, (RKey, str)):
            raise ValueError("Can only & between RKey and RKey/str/int")
        if isinstance(other, str):
            other = RKey(other)
        if other.target:
            raise ValueError("Only left RKey should have parameter")
        return RKey(self.name + '-' + other.name + ':' + self.target)


def RClass():
    def decorator(cls):
        class_name = cls.__name__
        for name, obj in vars(cls).items():
            if isinstance(obj, RKey) and not obj:
                setattr(cls, name, RKey(class_name + '.' + name))
        return cls

    return decorator
