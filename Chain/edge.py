class Edge:
	def __init__(self, ids, delay_req):
		self.ids = ids
		self.delay_req = delay_req
		self.location = {}
		self.mark = {}
		for i in ids:
			self.mark[i] = False

	def set_location(self, id, location):
		self.location[id] = location

	def get_location(self, id):
		return self.location[id]