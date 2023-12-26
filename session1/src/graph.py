from typing import List, Tuple, NewType

NodeID = NewType("NodeID", int)
NodeT = NewType("NodeT", float)
ConsumingTime = NewType("ConsumingTime", float)
EdgeID = NewType("EdgeID", int)

from collections import namedtuple

ROADLINE = namedtuple("ROADLINE", ["length", "speed", "proirity", "breakEventList"])
BREAK_EVENT = namedtuple("BREAK_EVENT", ["speed", "start_time", "end_time"])
from collections import defaultdict
from session1.session1Utils.utils import Search_Node, Edge
from copy import deepcopy

break_level = {1: 0.8, 2: 0.6, 3: 0.4, 4: 0.2, 5: 0.1}


class graph_static:
    def __init__(self, parsedGraph=None):
        if parsedGraph is not None:
            self.edge = parsedGraph["parsed_adj"]
        else:
            raise RuntimeError
        self.ex_cost = defaultdict(lambda: defaultdict(int))
        self.ex_cost_bak = deepcopy(self.ex_cost)
        self.ex_cost_unit = 0
        self.pre_target = None
        self.heuristic_dict = None
        self.node_constrain = None

    
    def get_neighbors(self, node_info):
        if node_info.nodeID in self.edge:
            Adj = self.edge[node_info.nodeID]
            results = []
            for neighbor in Adj:
                road_line = Adj[neighbor]
                t = road_line.length/road_line.speed + 0
                ex = self.ex_cost[node_info.nodeID][neighbor]*self.ex_cost_unit
                if self.node_constrain is not None and neighbor in self.node_constrain["nodes"]:
                    results.append(Search_Node(neighbor,node_info.g+t+ex - self.node_constrain["constrain_unit"],node_info.time_info+t,Edge(node_info.nodeID,neighbor)))
                else:
                    results.append(Search_Node(neighbor,node_info.g+t+ex,node_info.time_info+t,Edge(node_info.nodeID,neighbor)))
            return results
        else:
            print("no_neighbor")
            return []
            
    def set_node_constrain(self, nodes, constrain_unit):
        # return
        self.node_constrain = {"constrain_unit":constrain_unit, "nodes":nodes}

    def add_node_constrain(self, nodes, constrain_unit):
        # return
        assert isinstance(self.node_constrain, dict)
        self.node_constrain["constrain_unit"] = 0
        # self.node_constrain["constrain_unit"] = constrain_unit
        self.node_constrain["nodes"]|=nodes

    def heuristic(self, A, B):
        return 0
        if B == self.pre_target:
            return self.heuristic_dict[A]
        else:
            return 0

    def add_edge_cost(self, edge):
        a, b = edge
        self.ex_cost[a][b] += 1
        self.ex_cost[b][a] += 1
        assert self.ex_cost[a][b] == self.ex_cost[b][a]

    def compute_priority(self, edge_info, i):
        return 1 / (i + 1)

    def _getPathLen(self, edges):
        L = 0
        for e1, e2 in edges:
            L += self.edge[e1][e2].length
        return L

    def compute_overlap(self, path1, path2):
        def calculate(a,b):
            if b == 0:
                return 0
            return a/b 
        edges1 = set(path1.edges)
        edges2 = set(path2.edges)
        fenmu_1 = self._getPathLen(edges1)
        fenmu_2 = self._getPathLen(edges2)
        fenmu_0 = min(fenmu_1, fenmu_2)
        fenzi = self._getPathLen(edges1 & edges2)
        return calculate(fenzi, fenmu_0), (calculate(fenzi, fenmu_1), calculate(fenzi, fenmu_2))

    def reset(self):
        self.ex_cost_unit = 0
        self.ex_cost = deepcopy(self.ex_cost_bak)
        self.node_constrain = None


class graph_esx(graph_static):
    def __init__(self, static_info) -> None:
        super(graph_esx, self).__init__(static_info)

    @staticmethod
    def isinBreak(road_line, t):
        return road_line.breakEventList[0].start_time <= t < road_line.breakEventList[0].end_time

    def get_neighbors(self, node_info: Tuple[NodeID, NodeT]) -> List[Tuple[NodeID, NodeT, ConsumingTime, EdgeID]]:
        """
        输入：node:Tuple[NodeID,NodeT] 如(3,3.1),其中3为结点ID,3.1为从起点到结点3所需的最短时间
        输出：返回值为List[Tuple[NodeID,NodeT,ConsumingTime,EdgeID]]，列表中每个元素类型为元组Tuple，元组内第一个元素为与node邻接的结点ID，第三个元素为从输入node到当前node所需的时间，第二个元素为输入node的NodeT加ConsumingTime,第四个元素为从输入node到当前node所走的边的ID

        举例：
        输入：(3,5)
        结点4与3邻接，边ID为45，无动态限制，3，4间距离为10，速度限制为10，则结果为(4,5+1,1,45),即(4,6,1,45)
        结点233与3邻接，边ID为996，有动态约束，3，233间距离为15，在0~10s内速度限制为1，10s后速度限制为10，则从3往233走，先以1的速度移动(10-5)s,再以10的速度移动(15-1*5)/10=1s,总共移动1+5=6s,则结果为(233,5+6,6,996),即(233,11,6,996)
        没有其他结点与3邻接
        输出（return）：[(4,6,1,45),(233,11,6,996)]
        """
        if node_info.nodeID in self.edge:
            Adj = self.edge[node_info.nodeID]
            results = []
            for neighbor in Adj:
                road_line = Adj[neighbor]
                if road_line.breakEventList is not None and self.isinBreak(road_line, node_info.time_info):
                    break_info = road_line.breakEventList[0]
                    # 未处理 break_info.end_time is float("inf")的情况
                    if (break_info.end_time - node_info.time_info) * break_info.speed > road_line.length:
                        t = road_line.length/break_info.speed
                    elif break_info.speed==0:
                        continue
                    else:
                        t = (road_line.length - (break_info.end_time - node_info.time_info) * break_info.speed)/road_line.speed + break_info.end_time
                else:
                    t = road_line.length / road_line.speed
                ex = self.ex_cost[node_info.nodeID][neighbor]*self.ex_cost_unit
                if self.node_constrain is not None and neighbor in self.node_constrain["nodes"]:
                    results.append(Search_Node(neighbor,node_info.g+t+ex - self.node_constrain["constrain_unit"],node_info.time_info+t,Edge(node_info.nodeID,neighbor)))
                else:
                    results.append(Search_Node(neighbor,node_info.g+t+ex,node_info.time_info+t,Edge(node_info.nodeID,neighbor)))

            return results

        else:
            print("no_neighbor")
            return []

