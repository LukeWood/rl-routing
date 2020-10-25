import uuid
import networkx as nx


class Packet():
    def __init__(self, sender, to, path=[]):
        self.id = str(uuid.uuid4())
        self.current = sender
        self.sender = sender
        self.to = to
        self.path = path

    def on_wire(self):
        return isinstance(self.current, tuple)

    def find_next_hop(self):
        if len(self.path) < 2:
            return -1
        return self.path[1]

    def hop(self, target, graph):
        self.current = (self.current, target)
        self.path = nx.shortest_path(graph, target, self.to)

    def continue_on_wire(self, graph):
        f, t = self.current
        self.current = t

    def done(self):
        return self.current == self.to
