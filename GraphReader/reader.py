import csv
from network.links import Links
from network.nodes import Nodes
from gurobipy import *

def read_network(file):
	node_ids, node_cpu= [], {}
	link_ids, link_bw, link_delay = [], {}, {}

	with open(file, "r") as network_file:
		reader = csv.reader((row for row in network_file if not row.startswith("#")), delimiter=" ")
		for row in reader:
			row = remove_empty_values(row)

			if len(row) == 2:  # nodes: id, cpu
				node_id = row[0]
				node_ids.append(node_id)
				node_cpu[node_id] = float(row[1])

			if len(row) == 4:  # arcs: src_id, sink_id, cap, delay
				ids = (row[0], row[1])
				link_ids.append(ids)
				link_bw[ids] = float(row[2])
				link_delay[ids] = float(row[3])

	nodes = Nodes(node_ids, node_cpu)
	link_ids = tuplelist(link_ids)
	links = Links(link_ids, link_bw, link_delay)
	return nodes, links


def remove_empty_values(line):
	result = []
	for i in range(len(line)):
		if line[i] != "":
			result.append(line[i])
	return result