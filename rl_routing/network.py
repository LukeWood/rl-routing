import networkx as nx
import matplotlib.pyplot as plt
import random
import uuid
from collections import defaultdict

FREE = 0
OCCUPIED = 1


class Packet():
    def __init__(self, sender, to, path=[]):
        self.id = str(uuid.uuid4())
        self.current = sender
        self.sender = sender
        self.to = to
        self.path = list(reversed(path))

    def next_hop(self):
        return self.path[-1]

    def hop(self, target):
        self.current = target
        self.path.pop()

    def done(self):
        return self.current == self.to


class NetworkEnv():
    def __init__(self, graph=None):
        self.nodes = len(graph.nodes)
        self.graph = graph
        self.packets = {}
        self.completed_packets = 0

        nx.set_node_attributes(self.graph, {})

    def generate_packet(self, generate_path=True):
        sender = random.choice(range(self.nodes))
        to = random.choice(range(self.nodes))
        path = []
        if generate_path:
            try:
                path = nx.shortest_path(self.graph, sender, to)
            except (nx.exception.NetworkXNoPath):
                return None
        return Packet(sender, to, path=path)

    def create_packets(self, n=10):
        for _ in range(n):
            p = self.generate_packet()
            if p is None:
                continue
            self.packets[p.id] = p

    def render(self):
        pos = nx.get_node_attributes(self.graph, 'pos')
        node_color = [FREE for _ in range(self.nodes)]
        for packet in self.packets.values():
            node_color[packet.current] = OCCUPIED

        options = {
            "node_color": node_color,
            "cmap": plt.get_cmap('coolwarm'),
        }
        nx.draw(self.graph, pos, **options)

    def done(self):
        return len(self.packets.keys()) == 0

    def step(self):
        wires = defaultdict(lambda: defaultdict(lambda: False))

        for packet_key in list(self.packets.keys()):
            if packet_key not in self.packets:
                continue
            packet = self.packets[packet_key]
            cur = packet.current
            n = packet.next_hop()
            if wires[cur][n]:
                continue

            wires[cur][n] = True

            packet.hop(n)
            if packet.done():
                del self.packets[packet.id]
                self.completed_packets += 1
