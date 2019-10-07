from abc import ABC, abstractmethod


class Node:
    def __init__(self, id, label, group):
        self.id = id
        self.label = label
        self.group = group

    def __eq__(self, other):
        return self.id == other.id

    def __hash__(self):
        return hash(self.id)


class DrawableNode(ABC):
    def __init__(self):
        super().__init__()

    @abstractmethod
    def getNode(self):
        pass


class Edge:
    def __init__(self, from_, to, label):
        self.from_ = from_
        self.to = to
        self.label = label

    def __eq__(self, other):
        return self.from_ == other.from_ and self.to == other.to and self.label == other.label

    def __hash__(self):
        return hash(self.from_ + self.to + self.label)
