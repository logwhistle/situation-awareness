from typing import List,Tuple,NewType
NodeID = NewType("NodeID",int)
NodeT = NewType("NodeT",float)
ConsumingTime = NewType("ConsumingTime",float)
EdgeID = NewType("EdgeID",int)
import heapq
from session2.path_planning.utils import PATH, Search_Node


class AStar:
    def __init__(self, graph):
        self.graph = graph

    def reconstruct_path(self, came_from, current):
        total_path = [current.nodeID]
        people = [current.nodeID]
        edges = []
        while current in came_from.keys():
            edges.append(current.edgeID)
            current = came_from[current]
            total_path.append(current.nodeID)
            if current.nodeID>=10000:
                people.append(current.nodeID)
        return PATH(nodes=tuple(total_path[::-1]), edges=tuple(edges[::-1]), people=tuple(people[::-1]))



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
            # if n_nodes == 13:
            #     from visulization import draw_graph
            #     draw_graph(self.graph)
        return None
