from .model import Model


class Header(Model):
    def __init__(self, key: str, value: str):
        self.key = key
        self.value = value

    @classmethod
    def from_json(cls, json_item):
        for k, v in json_item.items():
            return cls(key=k, value=v)
        return cls(key=json_item['header'], value=json_item['value'])
    def __str__(self):
        return self.key
