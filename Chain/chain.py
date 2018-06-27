import Chain.edge as Edges
import Chain.instances as Instances

class Chain:
	def __init__(self, chain_id, flow_size, mobility, instances, edges):
		self.id = chain_id
		self.flow_size = flow_size
		self.mobility = mobility 	# mobility: user_residence_time, service_living_time
		self.instances = instances
		self.edges = edges

	def set_node_location(self, id, location):
		self.instances.set_location(id, location)

	def set_edge_location(self, id, location):
		self.edges.set_location(id, location)
