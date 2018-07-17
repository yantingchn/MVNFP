from operator import itemgetter, attrgetter
from itertools import islice
import networkx as nx
from math import ceil
import copy

def SFCR_embedding(g, c):

	v = c.get_node_location("0")	
	D = []
	kappa = c.mobility[1]/c.mobility[0]
	embedding_success = True
	
	for i in c.instances.ids:
		grade = []
		if i is not "0":
			for l in g[v]:
				if (check_delay(g[v][l]["delay"], c.edges.delay_req[(j, i)]) 
				and (g.nodes[l]["cpu"] - g.nodes[l]["u_c"]) >= c.instances.cpu[i] 
				and (g[l][v]["bw"]-g[l][v]["u_b"]) >= c.flow_size
				and l not in D):
					grade.append( (l, embedding_grade(g.nodes[l]["cpu"], g[l][v]["bw"], g.nodes[l]["u_c"], g[l][v]["u_b"], kappa)) )

			if (g.nodes[v]["cpu"] - g.nodes[v]["u_c"]) >= c.instances.cpu[i]:
				grade.append( (v, embedding_grade(g.nodes[v]["cpu"], float("Inf"), g.nodes[v]["u_c"], 0.0, kappa)) )

			if len(grade) == 0:
				embedding_success = False
				break
			
			grade = sorted(grade, key=itemgetter(1))
			tmp_node = []
			tmp_node.append(grade[0][0])
			for index in range(1,len(grade)):
				if grade[index][1] == grade[0][1]:
					tmp_node.append(grade[index][0])
			
			u = grade[0][0]
			if v in tmp_node:
				u = v
			
			print("chain",c.chain_id, "instance", i, "grade", grade)

			if u == v:
				g.nodes[v]["u_c"] += c.instances.cpu[i]
				c.set_node_location(i, v)
				c.instances.mark[i] = True
				c.set_edge_location((j, i), [(v, v)])
				c.edges.mark[(j, i)] = True
			else:
				g.nodes[u]["u_c"] += c.instances.cpu[i]
				c.set_node_location(i, u)
				c.instances.mark[i] = True
				g[u][v]["u_b"] += c.flow_size
				c.set_edge_location((j, i), [(v, u)])
				c.edges.mark[(j, i)] = True
				D.append(v)
				v = u

		j = i

	if not embedding_success:
		release_resource(g, c)

	return embedding_success


def SFCR_migration(g, c):
	migration_success = False
	
	v = c.get_node_location("0")
	u = c.get_node_location("1")
	w = c.get_node_location(c.instances.ids[-1])
	k = 10

	# for a, b in c.get_edge_location(("0", "1")):
	# 	if a != b:
	# 		g[a][b]["u_b"] -= c.flow_size
	# c.set_edge_location(("0", "1"), [])

	# p = nx.shortest_path(g, source = v, target = u, weight="delay")

	# path_delay = 0
	# for i in range(1,len(p)):
	# 	path_delay += g[p[i-1]][p[i]]["delay"]
	# 	if (g[p[i-1]][p[i]]["bw"] - g[p[i-1]][p[i]]["u_b"]) < c.flow_size:
	# 		migration_success = False

	# if check_delay(path_delay, c.edges.delay_req[("0", "1")]):
	# 	migration_success = False

	# if migration_success: 
	# 	new_edge = []
	# 	for i in range(1,len(p)):
	# 		g[p[i-1]][p[i]]["u_b"] += c.flow_size
	# 		new_edge.append((p[i-1],p[i]))
	# 	c.set_edge_location((u, v), new_edge)

	# 	for i in c.edges.ids:
	# 		c.edges.mark[i] = True
	# 	for i in c.instances.ids:
	# 		c.instances.mark[i] = True

	# else: # Migration Part
	original_path = []
	for i in c.instances.ids:
		original_path.append(c.get_node_location(i))

	# Clear original flow
	for e in c.edges.ids:
		# if e[0] == "0" and e[1] == "1":
		# 	continue
		for a, b in c.get_edge_location(e):
			if a != b:
				g[a][b]["u_b"] -= c.flow_size

	# Clear original VNF
	for i in c.instances.ids:
		if i == "0":
			continue
		g.nodes[c.get_node_location(i)]["u_c"] -= c.instances.cpu[i]

	print("After clear flow ---------------")
	print(g.nodes(data=True))
	print(g.edges(data=True))



	path_set = k_shortest_paths(g, v, w, k, "delay")
	evaluated_path_set = []
	for i in range(0, len(path_set)):
		evaluated_path_set.append([compare_paths(original_path, path_set[i]), path_set[i]])

	evaluated_path_set = sorted(evaluated_path_set,key=lambda l:l[0])


	mig_t = []
	g_c_set = []

	for i in range(0, len(evaluated_path_set)):
		g_tmp = copy.deepcopy(g)
		c_tmp = copy.deepcopy(c)
		if mig_time_for_dif_path(g_tmp, c_tmp, evaluated_path_set[i][1]):
			mig_t.append(c_tmp.mig_span)
			g_c_set.append((g_tmp, c_tmp))

	# Check migration success
	if len(mig_t) != 0: 
		migration_success = True
		index = mig_t.index(min(mig_t))
		g, c = g_c_set[index]
	# input()

	return migration_success, g, c


def embedding_grade(cap, bw, u_c, u_b, k):
	return u_c/cap + k*u_b/bw

def mig_time_for_dif_path(g, c, p):
	mig_success = True
	prev_vnf = "0"
	for n in c.instances.ids:
		if n == '0':
			c.instances.mark[n] = True
			continue
		cur_loc = c.get_node_location(n)
		tmp_path = []
		tmp_mig_t = []
		for m in p:
			tmp_path.append(m)

			# check link feasibility
			if not check_path_delay(g, tmp_path, c.edges.delay_req[(prev_vnf, n)]):
				continue
			if not check_path_resource(g, tmp_path, c.flow_size):
				continue
			if not check_node_resource(g, m, c.instances.cpu[n]):
				continue

			print("1")
			allocate_flow(g, tmp_path, c.flow_size)
			allocate_vnf(g, m, c.instances.cpu[n])
			m_t, mig_f, s_p = mig_time(g, cur_loc, m, c.instances.cpu[n])

			release_flow(g, tmp_path, c.flow_size)
			release_vnf(g, m, c.instances.cpu[n])

			if m_t > c.mobility[0]:
				print("m_t > T_r", m_t)
				continue

			tmp_mig_t.append((m_t, mig_f, s_p, copy.deepcopy(tmp_path))) # 0 mig_time, 1 mig_flow, 2 sp_mig_path, 3 new edge loc

		if len(tmp_mig_t) == 0:
			mig_success = False
			break
		else:
			tmp_mig_t = sorted(tmp_mig_t)
			m_t, mig_f, s_p, c_p = tmp_mig_t[0]

			print("n","m_t","mig_f","s_p", "c_p (", n, ")", tmp_mig_t[0])
			print("2")
			print(g.nodes(data=True))
			print(g.edges(data=True))
			allocate_flow(g, c_p, c.flow_size)
			c.set_edge_location((prev_vnf, n), path_to_edges(c_p))
			c.edges.mark[(prev_vnf, n)] = True
			allocate_vnf(g, c_p[-1], c.instances.cpu[n])
			c.set_node_location(n, c_p[-1])
			c.instances.mark[n] = True

			if c.mig_span < ceil(m_t):
				c.mig_span = ceil(m_t) 

			print("3")
			print(g.nodes(data=True))
			print(g.edges(data=True))
			allocate_flow(g, s_p, mig_f) # allocate mig traffic
			c.mig_links[n] = path_to_edges(s_p)
			c.mig_traffic[n] = mig_f


		prev_vnf = n

	return mig_success



# Define mig bw = 1/2 of residual bw
def mig_time(g, n, m, vnf_size):
	sp = []
	mig_t = 0.0
	flow_size = 0.0
	if n == m:
		mig_t = 0.0
		flow_size = 0.0
		sp = [n]
	else:
		sp = nx.shortest_path(g, source = n, target = m)
		edge_u = []
		for i in range(1, len(sp)):
			edge_u.append(g[sp[i-1]][sp[i]]["bw"] - g[sp[i-1]][sp[i]]["u_b"])

		flow_size = min(edge_u)/2.0
		if flow_size == 0:
			mig_t = float("Inf")
		else:
			mig_t = vnf_size/flow_size

	return mig_t, flow_size, sp

def path_to_edges(p):
	edges = []
	if len(p) == 1:
		edges.append((p[0], p[0]))
	else:
		for i in range(1, len(p)):
			edges.append((p[i-1], p[i]))

	return edges

def check_path_delay(g, p, delay_req):
	d = 0
	if len(p) > 1:
		for i in range(1, len(p)):
			d += g[p[i-1]][p[i]]["delay"]

	return (d < delay_req)
def check_path_resource(g, p, f):
	suf = True
	if len(p) > 1:
		for i in range(1, len(p)):
			if (g[p[i-1]][p[i]]["bw"] - g[p[i-1]][p[i]]["u_b"]) < f:
				suf = False
				break
	return suf

def check_node_resource(g, n, vnf_size):
	return (g.nodes[n]["cpu"] - g.nodes[n]["u_c"]) >= vnf_size

def allocate_flow(g, p, f):
	if len(p) > 1:
		for i in range(1, len(p)):
			if g[p[i-1]][p[i]]["u_b"] < 0:
				print(g[p[i-1]][p[i]]["u_b"])
				print(p)
				input()
			g[p[i-1]][p[i]]["u_b"] += f

def allocate_vnf(g, m, vnf_size):
	if g.nodes[m]["u_c"] < 0:
		input()
	g.nodes[m]["u_c"] += vnf_size

def release_flow(g, p, f):
	if len(p) > 1:
		for i in range(1, len(p)):
			g[p[i-1]][p[i]]["u_b"] -= f
			if g[p[i-1]][p[i]]["u_b"] < 0:
				print(p[i-1], p[i])
				input()

def release_vnf(g, m, vnf_size):
	g.nodes[m]["u_c"] -= vnf_size

def compare_paths(p1, p2):
	return float(len(list( set(p1) | set(p2) ))) / float((len(p1) + len(p2)))

def k_shortest_paths(g, source, target, k, weight=None):
    return list(islice(nx.shortest_simple_paths(g, source, target, weight=weight), k))

def check_delay(delay, link_delay_req):
    feasible = True
    if delay > link_delay_req:
    	feasible = False
    return feasible


def release_resource(g, c):
	for i in c.instances.ids:
		if c.instances.mark[i]:
			g.nodes[c.get_node_location(i)]["u_c"] -= c.instances.cpu[i]
			c.instances.mark[i] = False
	for i in c.edges.ids:
		if c.edges.mark[i]:
			for a, b in c.get_edge_location(i):
				if a != b:
					g[a][b]["u_b"] -= c.flow_size
			c.edges.mark[i] = False

def release_mig_resource(g, c):
	print("release mig traffic")
	for key in c.mig_links:
		for a,b in c.mig_links[key]:
			if a == b:
				continue
			g[a][b]["u_b"] -= c.mig_traffic[key]

	c.mig_links = {}
	c.mig_traffic = {}

# Jin Y. Yen, “Finding the K Shortest Loopless Paths in a Network”, Management Science, Vol. 17, No. 11, Theory Series (Jul., 1971), pp. 712-716.


