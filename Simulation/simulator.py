from random import expovariate, choice

def next_time(arrival_rate):
	next_time = round(expovariate(1.0/arrival_rate))
	while next_time < 1.0:
		next_time = round(expovariate(1.0/arrival_rate))
	return next_time

def random_move(g, c):
	c.reset_mark()
	cur_pos = c.get_node_location("0")
	next_pos = choice(list(g[cur_pos].keys()))
	c.set_node_location("0", next_pos)
	c.instances.mark["0"] = True
	print("chain_id", c.chain_id, "move",cur_pos, "to", next_pos)
	


