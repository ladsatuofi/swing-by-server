class EventModel:
    def __init__(self, name: str, description: str, location: str, time: int, time_str: str, tags: list, uuid=''):
        self.name = name
        self.description = description
        self.location = location
        self.time = time
        self.timeStr = time_str
        self.tags = tags
        self.uuid = uuid
