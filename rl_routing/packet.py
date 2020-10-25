import uuid


class Packet():
    def __init__(self, sender, to, path=[]):
        self.id = str(uuid.uuid4())
        self.current = sender
        self.sender = sender
        self.to = to
        self.path = list(reversed(path))

    def on_wire(self):
        return isinstance(self.current, tuple)

    def find_next_hop(self):
        return self.path[-1]

    def hop(self, target):
        self.current = (self.current, target)
        self.path.pop()

    def continue_on_wire(self):
        f, t = self.current
        self.current = t

    def done(self):
        return self.current == self.to
