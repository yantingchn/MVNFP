import GraphReader.reader as Reader
import networkx as nx
import matplotlib.pyplot as plt

filename = "sample_network.csv"
nodes, links = Reader.read_network(filename)

#create graph

g = nx.Graph()

for i in nodes.ids:
	g.add_node(i, cpu = nodes.cpu[i])
for i in links.ids:
	print(i)
	g.add_edge(i[0], i[1], bw = links.bw[i], delay = links.delay[i])



print(g.nodes(data = True))
print(g.edges(data = True))

nx.draw_networkx(g)
plt.show()