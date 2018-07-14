class Links:
    def __init__(self, ids, bw, delay):
        self.ids = ids 
        self.bw = bw
        self.remain_bw = bw
        self.delay = delay

    def embed_link(self, link_id, link_bw, link_delay_req):
        embedded = False
        if self.remain_bw[link_id] > link_bw and check_delay(link_id, link_delay_req):
            self.remain_bw[link_id] -= link_bw
            embedded = True
        return embedded

    def check_delay(self, link_id, link_delay_req):
        feasible = True
        if delay[link_id] > link_delay_req:
            feasible = False
        return feasible

    def embed_mig_flow(self, link_id, mig_bw):
        embedded = False
        if self.remain_bw[link_id] > mig_bw:
            self.remain_bw[link_id] -= mig_bw
            embedded = True
        return embedded

