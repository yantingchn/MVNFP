class Instance:
	def __init__(self, ids, cpu):
		self.ids = ids
		self.cpu = cpu
		self.location = {}
		self.mark = {}
		for i in ids:
			self.mark[i] = False

	def set_location(self, id, location):
		self.location[id] = location

	def get_location(self, id):
		return self.location[id]




