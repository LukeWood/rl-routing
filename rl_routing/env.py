import networkx as nx
import random
from collections import defaultdict, OrderedDict
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np

from .packet import Packet

FREE = "blue"
OCCUPIED = "red"
JUST_COMPLETE = "lawngreen"


class NetworkEnv():
    def __init__(self, fig=None, graph=None):
        self.nodes = len(graph.nodes)
        self.graph = graph
        self.packets = OrderedDict()
        self.just_completed = []
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
            for nid in self.just_completed:
                node_color[nid] = JUST_COMPLETE

            edge_color = [OCCUPIED if (u, v) in occupied else FREE for (
                u, v) in self.graph.edges()]
            edge_weight = [3 for (u, v) in self.graph.edges()]

            options = {
                "node_color": node_color,
                "edge_color": edge_color,
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
        just_completed = []

        reward = 0
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
                    just_completed.append(packet.to)
                    del self.packets[packet.id]
                    reward += 1
                continue

            cur = packet.current
            n = packet.find_next_hop()
            if wires[cur][n]:
                continue

            wires[cur][n] = True

            packet.hop(n)

        self.just_completed = just_completed
        self.completed_packets += reward
        return self.create_observation(), reward, self.done(), {}

    def create_observation(self):
        # create one hot adjacency matrix
        adj_matrix = np.array(nx.adjacency_matrix(self.graph).todense())
        wires = np.zeros((self.nodes, self.nodes))
        packets = np.zeros((self.nodes, self.nodes))

        # create packet state
        packets_vals = self.packets.values()
        for i, packet in enumerate(packets_vals):
            val = (i+1)/len(packets_vals)
            if isinstance(packet.current, tuple):
                f, t = packet.current
                wires[f][t] = 1.0
            else:
                packets[packet.current][packet.to] = val

        return np.stack([adj_matrix, wires, packets], axis=0)
