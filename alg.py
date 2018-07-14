from operator import itemgetter, attrgetter

# Algorithm: Initialization 

# Select the first virtual node(closest to user) in SFCR as n_1st;
# Embed n_1st into the substrate node v_0 which is closest to PU; 
# Initialize queue q, enqueue n_1st to q;
# Initialize D as empty set;
# v <- v_0;
# while q is not empty do
# 	n = dequeue(q);
# 	for virtual link l connected to n do 
# 		if n' has not been embedded then
# 			n' <- the other endpoint of l;
# 			C <- {v' | adjacent substrate nodes of v & v} \ D;
# 			calculate omega for all v' in C;
# 			embed n' onto the v' with min omega, embed l onto the edge(v, v');
# 			enqueue n' to q, mark n' as embedded;
# 			if v' not equal to v then
# 				D = D U {v'};
# 				v <- v';
# 			end if
# 		end if
# 	end for
# end while


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
			u = grade[0][0]

			if u == v:
				g.nodes[v]["u_c"] += c.instances.cpu[i]
				c.set_node_location(i, v)
				c.instances.mark[i] = True
				c.set_edge_location((j, i), (v, v))
				c.edges.mark[(j, i)] = True
			else:
				g.nodes[u]["u_c"] += c.instances.cpu[i]
				c.set_node_location(i, v)
				c.instances.mark[i] = True
				g[u][v]["u_b"] += c.flow_size
				c.set_edge_location((j, i), (v, u))
				c.edges.mark[(j, i)] = True
				D.append(v)
				v = u

		j = i

	if not embedding_success:
		release_resource(g, c)

	return embedding_success

# Algorithm: Handover

# {p_i} <- {all paths that origin from v_0 & path delay < SFCR's requirement};
# Calculate gamma value for all paths in {p_i};
# Sort out {p_i} increasingly according to gamma;
# stop <- false;
# i <- 1;

# while (stop = false) & (i < N_max) do
# 	Select the first virtual node(closest to user) in SFCR as n_1st;
# 	Initialize queue q1, enqueue n_1st into q;
# 	success <- true;
# 	while q is not empty do
# 		n = dequeue(q);
# 		if (n not satisfies SFCR's requirement) or (n not allocated on p_i) then
# 			choose feasible substrate node v on p_i with min omega;
# 			migrate n and its attached link onto p_i with min lamda;
# 			if failed migration then 
# 				success <- false;
# 				break;
# 			end if
# 		end if
# 		mark n as migrated;
# 		n' <- the node shares same edge with n and has not been migrated;
# 		enqueue n' to q;
# 	end while
# 	if success then
# 		stop <- true;
# 	else 
# 		i <- i+1;
# 	end if
# end

def SFCR_migration(g, c):
	
	return True


def embedding_grade(cap, bw, u_c, u_b, k):
	return u_c/cap + k*u_b/bw

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
			a,b = c.get_edge_location(i)
			if a != b:
				g[a][b]["u_b"] -= c.flow_size
			c.edges.mark[i] = False

def release_mig_resource(g, c):
	for i in c.mig_links:
		g[i[0]][i[1]]["u_b"] -= c.mig_links[i]



