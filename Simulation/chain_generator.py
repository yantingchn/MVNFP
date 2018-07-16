from Chain.chain import Chain
from Chain.edge import Edge
from Chain.instances import Instance
from random import randint

def generator(chain_id, chain):
	mobility = random_mobility()
	instances = Instance(chain['node_ids'], chain['cpu'])
	edges = Edge(chain['edge_ids'], chain['delay_req'])
	chain = Chain(chain_id, chain['flow'], mobility, instances, edges)

	return chain



def random_mobility():
	# user_residence_time = float(randint(1,5)*10)
	# service_living_time = float(randint(1,5)*30)
	user_residence_time = 21.0
	service_living_time = 40.0

	return user_residence_time, service_living_time
