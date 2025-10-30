import json


class Model:
    RESOURCE_URL = ''

    id = None

    def __init__(self):
        pass

    def to_json(self):
        return json.dumps(self.__dict__, default=lambda o: o.__dict__)

    @classmethod
    def from_json(cls, json_item):
        pass
