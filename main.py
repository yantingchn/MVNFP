import GraphReader.reader as Reader
import Simulation.chain_generator as ChainGenerator
import networkx as nx
import matplotlib.pyplot as plt
from random import randint

network_filename = "parameters/sample_network.csv"
chain_filename = 'parameters/sample_chains.csv'
nodes, links = Reader.read_network(network_filename)
chain = Reader.read_chain(chain_filename)

print(chain[0])

#create graph

g = nx.Graph()

for i in nodes.ids:
	g.add_node(i, cpu = nodes.cpu[i])
for i in links.ids:
	g.add_edge(i[0], i[1], bw = links.bw[i], delay = links.delay[i])



# chain generator
# random number for chain type
# random mobility ratio (user residence time, service living time)
# return chain
idx = randint(0, len(chain)-1)
chain_id = 0
c = ChainGenerator.generator(chain_id, chain[idx])


# print(g.nodes(data = True))
# print(g.edges(data = True))
