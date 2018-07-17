import Chain.edge as Edges
import Chain.instances as Instances

class Chain:
	def __init__(self, chain_id, flow_size, mobility, instances, edges):
		self.chain_id = chain_id
		self.flow_size = flow_size
		self.mobility = mobility 	# mobility: user_residence_time, service_living_time
		self.instances = instances
		self.edges = edges
		self.mig_links = {}
		self.mig_traffic = {}
		self.mig_span = 0
		self.HO_timer = 0
		self.SE_timer = 0
		self.MIG_timer = 0



	def is_move(self):
		return (self.HO_timer >= self.mobility[0])

	def is_end(self):
		return (self.SE_timer >= self.mobility[1])

	def increase_timer(self):
		self.HO_timer += 1
		self.SE_timer += 1

	def increase_mig_timer(self):
		if self.mig_span != 0.0:
			self.MIG_timer += 1

	def is_mig_end(self):
		return ((self.MIG_timer >= self.mig_span) and self.mig_span != 0)

	def reset_mark(self):
		self.instances.reset_mark()
		self.edges.reset_mark()

	def reset_HO_timer(self):
		self.HO_timer = 0
	def reset_mig_timer(self):
		self.MIG_timer = 0
	def reset_mig_span(self):
		self.mig_span = 0.0

	def set_node_location(self, id, location):
		self.instances.set_location(id, location)

	def set_edge_location(self, id, location):
		self.edges.set_location(id, location)

	def get_node_location(self, id):
		return self.instances.get_location(id)
	def get_edge_location(self, id):
		return self.edges.get_location(id)

	def get_link_location(self, id):
		return self.edges.get_location(id)

	def get_service_living_time(self):
		return self.mobility[1]

	def get_user_residence_time(self):
		return self.mobility[0]

	def get_chain_id(self):
		return self.chain_id