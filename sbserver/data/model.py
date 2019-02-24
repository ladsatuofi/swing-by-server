class EventModel:
    def __init__(self, name: str, description: str, location: str, time: int, tags: list, uuid=''):
        self.name = name
        self.description = description
        self.location = location
        self.time = time
        self.tags = tags
        self.uuid = uuid
