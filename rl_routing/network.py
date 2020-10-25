import networkx as nx
import matplotlib.pyplot as plt
import random
import uuid
from collections import defaultdict
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np

FREE = 0
OCCUPIED = 1


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


class NetworkEnv():
    def __init__(self, fig=None, graph=None):
        self.nodes = len(graph.nodes)
        self.graph = graph
        self.packets = {}
        self.completed_packets = 0

        self.fig = fig
        if self.fig is None:
            self.fig = Figure(figsize=(8, 8))
        self.canvas = FigureCanvas(self.fig)

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

    def render(self, mode="rgb"):
        if mode == "rgb":
            pos = nx.get_node_attributes(self.graph, 'pos')
            occupied = {}
            for packet in self.packets.values():
                if isinstance(packet.current, tuple):
                    f, t = packet.current
                    occupied[(f, t)] = True
                    occupied[(t, f)] = True
                else:
                    occupied[packet.current] = True

            node_color = [
                OCCUPIED if index in occupied else FREE
                for index in range(self.nodes)
            ]
            edge_color = [OCCUPIED if (u, v) in occupied else FREE for (
                u, v) in self.graph.edges()]
            edge_weight = [3 for (u, v) in self.graph.edges()]

            options = {
                "node_color": node_color,
                "cmap": plt.get_cmap('coolwarm'),
                "edge_color": edge_color,
                "edge_cmap": plt.get_cmap('coolwarm'),
                "width": edge_weight,
            }
            ax = self.fig.gca()
            nx.draw(self.graph, pos, ax=ax, **options)
            self.canvas.draw()
            s, (width, height) = self.canvas.print_to_buffer()
            return np.fromstring(s, np.uint8).reshape((height, width, 4))
        raise f"Mode {mode} not supported."

    def done(self):
        return len(self.packets.keys()) == 0

    def step(self):
        wires = defaultdict(lambda: defaultdict(lambda: False))
        for packet in self.packets.values():
            if isinstance(packet.current, tuple):
                f, t = packet.current
                wires[f][t] = True

        for packet_key in list(self.packets.keys()):
            if packet_key not in self.packets:
                continue
            packet = self.packets[packet_key]

            # check if on wire
            if packet.on_wire():
                packet.continue_on_wire()
                if packet.done():
                    del self.packets[packet.id]
                    self.completed_packets += 1
                continue

            cur = packet.current
            n = packet.find_next_hop()
            if wires[cur][n]:
                continue

            wires[cur][n] = True

            packet.hop(n)
