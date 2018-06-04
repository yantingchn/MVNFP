import math


class Links:
        def __init__(self, ids, dr, delay):
                    self.ids = ids
                    self.dr = dr
                    self.delay = delay

        def weight(self, link):
                    if self.dr[link] == 0:
                        return math.inf
                    elif self.delay[link] == 0:
                        return 0
                    return 1 / (self.dr[link] + 1 / self.delay[link])
