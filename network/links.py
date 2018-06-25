class Links:
    def __init__(self, ids, bw, delay):
        #form [1,2]
        self.ids = ids 
        self.bw = bw
        self.delay = delay
        self.edges = []

    def used_bw(self):
        return sum(c.flow for c in self.edges)

    def remain_bw(self):
        return self.bw - sum(c.flow for c in self.chains)