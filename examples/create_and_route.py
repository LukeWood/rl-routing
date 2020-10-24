import matplotlib.pyplot as plt
import networkx as nx
import rl_routing
env = rl_routing.NetworkEnv(
    graph=nx.generators.geometric.random_geometric_graph(50, 0.2))
env.create_packets(n=10)
env.render()
plt.show()
