from typing import List,Tuple,NewType
NodeID = NewType("NodeID",int)
NodeT = NewType("NodeT",float)
ConsumingTime = NewType("ConsumingTime",float)
EdgeID = NewType("EdgeID",int)
import heapq
from session1.session1Utils.utils import PATH, Search_Node

from collections import defaultdict
def parse_gr():
    with open(r"E:\态势感知\code\map\real.gr", 'r') as f:
        adj_info = list(map(lambda args: (int(args[0]), int(args[1])) if (int(args[0])<int(args[1])) else (int(args[1]), int(args[0])),
                        [line.strip().split(" ") for line in f.readlines()]))
    
    adj_info = set(adj_info)
    adj = defaultdict(list)
    for e1,e2 in adj_info:
        assert e1<e2
        adj[e1].append(e2)
        adj[e2].append(e1)
    return adj
class test_graph:
    def __init__(self) -> None:
        self.edge = parse_gr()

    def get_neighbors(self,node_info):
        nodeID,node_t = node_info
        if nodeID in self.edge:
            neighbors = self.edge[nodeID]
            results = []
            for neighbor in neighbors:
                results.append((neighbor,node_t+1,1,(nodeID,neighbor)))

            return results

        else:
            print(nodeID)
            print("no_neighbor")
            return []
    def heuristic(self, a, b):
        return 0

class AStar:
    def __init__(self, graph):
        self.graph = graph

    def reconstruct_path(self, came_from, current):
        total_path = [current.nodeID]
        time_info = [current.time_info]
        edges = []
        while current in came_from.keys():
            edges.append(current.edgeID)
            current = came_from[current]
            total_path.append(current.nodeID)
            time_info.append(current.time_info)
            # if current.edgeID is not None:
            #     edges.append(current.edgeID)
        return PATH(nodes=tuple(total_path[::-1]), edges=tuple(edges[::-1]), time_info=tuple(time_info[::-1]))



    def search(self, start:NodeID, target:NodeID, recorder=None, start_time = 0):
        
        open_set = {start,}
        closed_set = set()

        came_from = {}

        g_score = {} 
        g_score[start] = 0
        open_heapq = [(self.graph.heuristic(start,target),Search_Node(start, 0, 0, None))]
        heapq.heapify(open_heapq)
        while open_set:
            f,current = heapq.heappop(open_heapq)
            if not current.nodeID in open_set:
                #排除重复点
                continue

            if current.nodeID==target:
                # record below
                if recorder is not None:
                    n_nodes = len(closed_set)
                    recorder.logger.info("searching {} nodes".format(n_nodes))
                    recorder.searching_nodes+=n_nodes
                    recorder.searching_times+=1
                # record above
                return self.reconstruct_path(came_from, current)

            open_set -= {current.nodeID}
            closed_set |= {current.nodeID}

            neighbor_list = self.graph.get_neighbors(current)
            
            for neighbor in neighbor_list:
                if neighbor.nodeID in closed_set:
                    continue
                
                # tentative_g_score = g_score.get(current, float("inf")) + neighbor_consuming_time

                if neighbor.nodeID not in open_set:
                    open_set |= {neighbor.nodeID}
                    heapq.heappush(open_heapq,(neighbor.g+self.graph.heuristic(neighbor.nodeID,target),neighbor))
                elif neighbor.g >= g_score.setdefault(neighbor, float("inf")):
                    continue
                else:
                    #会出现重复点
                    heapq.heappush(open_heapq,(neighbor.g+self.graph.heuristic(neighbor.nodeID,target),neighbor))
                came_from[neighbor] = current
                g_score[neighbor] = neighbor.g
        if recorder is not None:
            n_nodes = len(closed_set)
            recorder.logger.info("searching {} nodes -- searching failed".format(n_nodes))
            recorder.searching_nodes+=n_nodes
            recorder.searching_times+=1
        return None

if __name__=="__main__":
    from itertools import combinations
    from graph import graph_static
    graph = graph_static()
    path_finder = AStar(graph)
    path = path_finder.search(756,300)
    print(path)
    nodes = path.nodes
    __nodes = tuple(x for x,_ in path.edges)+(path.edges[-1][-1],)
    print(nodes)
    print(__nodes)
    print(nodes==__nodes)

    # for start, target in combinations(graph.edge.keys(), 2):
    #     path = path_finder.search(start,target)
    #     if path is None:
    #         print(start, target)