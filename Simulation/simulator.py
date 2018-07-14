from random import expovariate

def next_time(arrival_rate):
	next_time = round(expovariate(1.0/arrival_rate))
	while next_time < 1.0:
		next_time = round(expovariate(1.0/arrival_rate))
	return next_time
