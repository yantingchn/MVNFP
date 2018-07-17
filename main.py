import matplotlib.pyplot as plt
from random import randint
import numpy as np
import networkx as nx
import GraphReader.reader as Reader
import Simulation.chain_generator as ChainGenerator
import Simulation.simulator as Simulator
import alg

network_filename = "parameters/sample_network.csv"
chain_filename = 'parameters/sample_chains_test.csv'
nodes, links = Reader.read_network(network_filename)
chain_temp = Reader.read_chain(chain_filename)



#create graph
g = nx.Graph()
for i in nodes.ids:
	g.add_node(i, cpu = nodes.cpu[i], u_c = 0.0)
for i in links.ids:
	g.add_edge(i[0], i[1], bw = links.bw[i], delay = links.delay[i], u_b = 0.0)

nx.draw(g, with_labels=True, font_weight='bold')
plt.draw()


# Initial Var
cur_time = 0
chain_id = 0
n_t = 0
c = None

# simulation setting
user_arrival_rate = 1.0
simulation_time = 1000


Mig_SFCR = []
Embedded_SFCR = []
Fail_SFCR = []
Finish_SFCR = []
T_mig = 0.0
T_down = 0.0
T_down_2 = 0.0

# simulation
while cur_time < simulation_time:

	# SFCR init
	if n_t == 0.0:
		n_t = Simulator.next_time(user_arrival_rate)
		c = ChainGenerator.generator(chain_id, chain_temp[randint(0, len(chain_temp)-1)])
		c.set_node_location(str(0), str(randint(0, len(g)-1)))
		c.instances.mark[str(0)] = True
		chain_id += 1	
		
		print("---------------------------------------------------------------")
		print("SFCR init -> Current Time:", cur_time, "; Chain Id:", chain_id-1, "; UE Position:", c.get_node_location("0"))
		print("Embed SFCR",len(Embedded_SFCR))
		print("Fail_SFCR", len(Fail_SFCR))
		print("Mig_SFCR", len(Mig_SFCR))
		print("Finish_SFCR", len(Finish_SFCR))
		print("Nodes->",g.nodes(data=True))
		print("Edges->", g.edges(data=True))

	# Embedding
	if c is not None:
		if alg.SFCR_embedding(g, c):
			Embedded_SFCR.append(c)
		else:
			Fail_SFCR.append(c)
			T_down_2 += c.mobility[1]
		print("After embed")
		print("Nodes->",g.nodes(data=True))
		print("Edges->", g.edges(data=True))
		c = None


	remove_list_of_embed = []
	Mig_SFCR_tmp = []
	for s in range(0, len(Embedded_SFCR)):
		Embedded_SFCR[s].increase_timer()

		if Embedded_SFCR[s].is_end():
			print("Chain_id", Embedded_SFCR[s].chain_id, "is end at time", cur_time)
			alg.release_resource(g, Embedded_SFCR[s])
			alg.release_mig_resource(g, Embedded_SFCR[s])
			Finish_SFCR.append(Embedded_SFCR[s])
			remove_list_of_embed.append(s)

		elif Embedded_SFCR[s].is_move():
			Simulator.random_move(g, Embedded_SFCR[s])
			mig_sucess, g, Embedded_SFCR[s] = alg.SFCR_migration(g, Embedded_SFCR[s])
			if mig_sucess:
				Embedded_SFCR[s].reset_HO_timer()
				print("Chain id", Embedded_SFCR[s].chain_id, "HO at time", cur_time)
				if Embedded_SFCR[s].mig_span != 0:
					remove_list_of_embed.append(s)
					Mig_SFCR_tmp.append(Embedded_SFCR[s])
				T_mig += Embedded_SFCR[s].mig_span
				print("Nodes->",g.nodes(data=True))
				print("Edges->", g.edges(data=True))
			else:
				remove_list_of_embed.append(s)
				Fail_SFCR.append(Embedded_SFCR[s])
				T_down += Embedded_SFCR[s].mobility[1] - Embedded_SFCR[s].SE_timer
				print("Nodes->",g.nodes(data=True))
				print("Edges->", g.edges(data=True))

	remove_list_of_mig = []
	Embedded_SFCR_tmp = []
	for s in range(0, len(Mig_SFCR)):
		Mig_SFCR[s].increase_timer()
		Mig_SFCR[s].increase_mig_timer()
		if Mig_SFCR[s].is_end():
			print("Chain_id", Mig_SFCR[s].chain_id, "is end at time", cur_time)
			alg.release_resource(g, Mig_SFCR[s])
			alg.release_mig_resource(g, Mig_SFCR[s])
			remove_list_of_mig.append(s)
			Finish_SFCR.append(Mig_SFCR[s])
		elif Mig_SFCR[s].is_mig_end():
			print("Chain_id", Mig_SFCR[s].chain_id, "mig is end at time", cur_time)
			Mig_SFCR[s].reset_mig_timer()
			Mig_SFCR[s].reset_mig_span()
			alg.release_mig_resource(g, Mig_SFCR[s])
			remove_list_of_mig.append(s)
			Embedded_SFCR_tmp.append(Mig_SFCR[s])

	# Mig_end service -> Embed service
	# Embed service -> Mig_service
	for i in sorted(remove_list_of_embed, reverse=True):
		Embedded_SFCR.pop(i)
	for i in sorted(remove_list_of_mig, reverse=True):
		Mig_SFCR.pop(i)

	Embedded_SFCR = Embedded_SFCR + Embedded_SFCR_tmp
	Mig_SFCR = Mig_SFCR + Mig_SFCR_tmp


	n_t -= 1
	cur_time += 1


print("Finish:")
print("Embed SFCR",len(Embedded_SFCR))
print("Fail_SFCR", len(Fail_SFCR))
print("Mig_SFCR", len(Mig_SFCR))
print("Finish_SFCR", len(Finish_SFCR))
print("T_mig", T_mig)
print("T_down", T_down)
print("T_down_2", T_down_2)
print("Nodes->", g.nodes(data=True))
print("Edges->", g.edges(data=True))
print("AC Rate:", (len(Embedded_SFCR)+len(Finish_SFCR))/(len(Fail_SFCR)+len(Embedded_SFCR)+len(Finish_SFCR)))
