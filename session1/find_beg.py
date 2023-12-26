from collections import namedtuple
from session1.src.graph import graph_esx, graph_static

ROADLINE = namedtuple("ROADLINE", ["length", "speed"])
BREAK_INFO = namedtuple("BREAK_INFO", ["speed", "start_time", "end_time"])


class find_begin:
    def __init__(self, dynamic_time=0, paths=None, dynamic_graph=None):
        self.dynamic_time = dynamic_time
        self.paths = paths
        self.node0 = None
        self.node1 = None
        self.distance = 0
        self.t1 = 0
        self.t2 = 0
        self.count = 0
        self.results = []
        self.graph_esx = dynamic_graph

    def find(self):
        if not self.paths:
            return None
        for path in self.paths:
            for i, edge in enumerate(path.edges):
                roadline = self.graph_esx.edge[path.nodes[i]][path.nodes[i + 1]]
                length, speed = roadline.length, roadline.speed
                if self.count + length / speed < self.dynamic_time:
                    self.count += length / speed
                else:
                    self.node0 = path.nodes[i]
                    self.node1 = path.nodes[i + 1]
                    self.distance = (self.dynamic_time - self.count) * speed
                    self.t1, self.t2 = self.distance / speed, (length - self.distance) / speed
            self.results.append([self.node0, self.node1, self.t1, self.t2, self.distance])
        return self.results
