class Instance:
	def __init__(self, ids, cpu):
		self.ids = ids
		self.cpu = cpu
		self.location = {}

	def set_location(self, id, location):
		self.location[id] = location




