from typing import List, Tuple, NewType

NodeID = NewType("NodeID", int)
NodeT = NewType("NodeT", float)
ConsumingTime = NewType("ConsumingTime", float)
EdgeID = NewType("EdgeID", int)

from collections import namedtuple

ROADLINE = namedtuple("ROADLINE", ["length", "speed", "proirity"])
BREAK_INFO = namedtuple("BREAK_INFO", ["speed", "start_time", "end_time"])
from collections import defaultdict
from session2.path_planning.utils import Search_Node, Edge
from copy import deepcopy

break_level = {1: 0.8, 2: 0.6, 3: 0.4, 4: 0.2, 5: 0.1}


class graph_static:
    def __init__(self, parsedGraph=None):
        if parsedGraph is not None:
            self.edge = parsedGraph
        else:
            raise RuntimeError
        self.ex_cost = defaultdict(lambda: defaultdict(int))
        self.ex_cost_bak = deepcopy(self.ex_cost)
        self.ex_cost_unit = 0

    def get_neighbors(self, node_info):
        if node_info.nodeID in self.edge:
            neighbors = self.edge[node_info.nodeID]
            results = []
            for neighbor in neighbors:
                ex = self.ex_cost[node_info.nodeID][neighbor]*self.ex_cost_unit
                if neighbor<10000:
                    results.append(Search_Node(neighbor,node_info.g+1+ex,node_info.time_info+1,Edge(node_info.nodeID,neighbor)))
                else:
                    results.append(Search_Node(neighbor,node_info.g+10+ex,node_info.time_info+10,Edge(node_info.nodeID,neighbor)))
            return results

        else:
            print("no_neighbor")
            return []


    def heuristic(self, A, B):
        return 0

    def add_edge_cost(self, edge):
        a, b = edge
        self.ex_cost[a][b] += 1
        self.ex_cost[b][a] += 1
        assert self.ex_cost[a][b] == self.ex_cost[b][a]

    def compute_priority(self, *args):
        raise NotImplementedError

    def _getPathLen(self, edges):
        L = len(edges)
        return L

    def compute_overlap(self, path1, path2):
        edges1 = set(path1.edges)
        edges2 = set(path2.edges)
        return self._getPathLen(edges1 & edges2) / min(self._getPathLen(edges1), self._getPathLen(edges2))

    def reset(self):
        self.ex_cost_unit = 0
        self.ex_cost = deepcopy(self.ex_cost_bak)

