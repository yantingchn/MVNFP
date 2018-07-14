import GraphReader.reader as Reader
import Simulation.chain_generator as ChainGenerator
import Simulation.simulator as Simulator
import alg
import networkx as nx
import matplotlib.pyplot as plt
from random import randint
import numpy as np



network_filename = "parameters/sample_network.csv"
chain_filename = 'parameters/sample_chains.csv'
nodes, links = Reader.read_network(network_filename)
chain_temp = Reader.read_chain(chain_filename)



#create graph
g = nx.Graph()
for i in nodes.ids:
	g.add_node(i, cpu = nodes.cpu[i], u_c = 0.0)
for i in links.ids:
	g.add_edge(i[0], i[1], bw = links.bw[i], delay = links.delay[i], u_b = 0.0)



# simulation setting
user_arrival_rate = 5.0
simulation_time = 100
cur_time = 0
chain_id = 0
n_t = 0
c = None


Mig_SFCR = []
Embedded_SFCR = []
Fail_SFCR = []


# simulation
while cur_time < simulation_time:

	# SFCR init
	if n_t == 0.0:
		n_t = Simulator.next_time(user_arrival_rate)
		c = ChainGenerator.generator(chain_id, chain_temp[randint(0, len(chain_temp)-1)])
		c.set_node_location(str(0), str(randint(0, len(g)-1)))
		c.instances.mark[str(0)] = True
		chain_id += 1	
		
		print("SFCR init -> Current Time:", cur_time, "; Chain Id:", chain_id, "; UE Position:", c.get_node_location("0"))


	# Embedding
	if c is not None:
		if alg.SFCR_embedding(g, c):
			Embedded_SFCR.append(c)
		else:
			Fail_SFCR.append(c)

		c = None

	for s in Embedded_SFCR:
		s.increase_timer()

		if s.is_end():
			alg.release_resource(g, s)
			Embedded_SFCR.remove(s)
		elif s.is_move():
			
			if alg.SFCR_migration(g, s):
				s.reset_HO_timer()
			else:
				Embedded_SFCR.remove(s)
				Fail_SFCR.append(s)

	for s in Mig_SFCR:
		if s.is_mig_end():
			s.reset_mig_timer()
			s.reset_mig_span()
			alg.release_mig_resource(g, s)

	
	n_t -= 1
	cur_time += 1



print(len(Embedded_SFCR))
print(len(Fail_SFCR))


