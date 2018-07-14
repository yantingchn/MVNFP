class Nodes:
    def __init__(self, ids, cpu):
        self.ids = ids
        self.cpu = cpu
        self.remain_cpu = cpu

    def embed_ndoe(self, node_id, node_cpu):
    	embedded = False
    	if self.remain_cpu[node_id] > node_cpu:
    		self.remain_cpu[node_id] -= node_cpu
    		embedded = True
    	return embedded

    def remove_node(self, node_id, cpu):
    	self.remain_cpu[node_id] += cpu
    	if self.remain_cpu[node_id] > self.cpu[node_id]:
    		print("Error: node:", node_id, " exceed cpu limit")

    def get_remain_cpu(self, id):
    	return self.remain_cpu[id]

    def get_cpu(self, id):
        return self.cpu[id]



