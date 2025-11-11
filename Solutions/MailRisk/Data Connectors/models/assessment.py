from .model import Model


class Assessment(Model):
    def __init__(self, risk: int, category: str, confidence: float, source: str, source_id: int, assessed_at: str):
        self.risk = risk
        self.category = category
        self.confidence = confidence
        self.source = source
        self.source_id = source_id
        self.assessed_at = assessed_at

    @classmethod
    def from_json(cls, json_item):
        return cls(risk=json_item['risk'],
                   category=json_item['category'],
                   confidence=json_item['confidence'],
                   source=json_item['source'],
                   source_id=json_item['source_id'],
                   assessed_at=json_item['assessed_at'])

    def __str__(self):
        return self.category
