from pprint import pformat
from session1.src.shortest_path_finding import AStar
from itertools import combinations
import numpy as np
from session1.session1Utils.utils import PATH, Prioritized_Edge, Init_State, Search_Node

MAX_ITER = 500
UNIT_RATIO = 1
print_flag = False
if not print_flag:
    def print(*args, **kargs):
        pass


class esx_base:
    def __init__(self, graph) -> None:
        self.graph = graph
        self.path_finding = AStar(graph)
        self.meta_info = {}

    def compute_overlap(self, path1, path2):
        return self.graph.compute_overlap(path1, path2)[0]

    def compute_overlap_specifically(self, path1, path2):
        return self.graph.compute_overlap(path1, path2)

    def compute_priority(self, edge_info):
        """
        Let starts be all the nodes which are the starting points of all incoming edges to the source of the given edge.
        Let Target be all the nodes which are the ending points of all outgoing edges from the target of the given edge.
        This function returns the number of shortest paths from some source to some target that contain the given edge.
        """
        e1, e2 = edge_info
        proirity_init = self.graph.edge[e1][e2].proirity
        # 此处假设图为无向图 同时还为考虑加入动态信息
        # TODO 处理以上问题
        neighbor_list = self.graph.get_neighbors(Search_Node(e1, 0, 0, None))
        starts = [ID for ID, *_ in neighbor_list if ID != e2]
        neighbor_list = self.graph.get_neighbors(Search_Node(e2, 0, 0, None))
        targets = [ID for ID, *_ in neighbor_list if ID != e1]
        priority = 0.1
        for start in starts:
            for target in targets:
                # if start==target:
                #     continue
                path = self.path_finding.search(
                    start=start, target=target)
                if path is not None and (edge_info in path.edges):
                    priority += 1
        return priority + proirity_init*20  # 最大

    @staticmethod
    def select(edges):
        return max(edges)
        p = np.array([edge.priority/((edge.rank+1)*50) for edge in edges])
        p = np.exp(p)/np.exp(p).sum()
        index = np.random.choice(np.arange(len(edges), dtype=np.int), p = p)
        return edges[index]

    def search(self, start, target, k=10, overlap_theta=0.1, init_state=None, recorder=None):
        raise NotImplementedError


class esx(esx_base):

    def search(self, start, target, k=10, overlap_theta=0.1, init_state=None, recorder=None):
        if init_state is None:
            resPaths = []

            path = self.path_finding.search(
                start, target, recorder)
            assert path is not None, "start:{} target:{} ".format(start, target)
            resPaths.append(path)

            if k == 1:
                return resPaths
        else:
            resPaths = init_state

        pathEdges_set = [dict() for _ in range(len(resPaths))]

        for idx, path in enumerate(resPaths):
            for edgeID in path.edges:
                pathEdges_set[idx][edgeID] = Prioritized_Edge(
                    priority=self.compute_priority(edgeID), edge=edgeID, idx=idx)

        # overlaps 当前路径与之前搜索到的路径的重合度
        overlaps = [1]*len(resPaths)
        possible = True

        self.graph.ex_cost_unit  = path.time_info[-1]*(1+UNIT_RATIO)
        self.graph.set_node_constrain(nodes = set(path.nodes[1:-2]), constrain_unit = path.time_info[-1]*UNIT_RATIO/len(path.nodes))
        while (len(resPaths) < k and possible):
            iter_num = 0
            olRatio = 1

            # record below
            if recorder is not None:
                recorder.logger.info(
                    "new path : {}".format(pformat(resPaths[-1])))
                recorder.logger.info("overlaps : {}".format(overlaps))

            # record above

            while olRatio > overlap_theta:
                iter_num += 1
                if iter_num > MAX_ITER:
                    return resPaths
                # 找到当前路径与哪个路径重合度最高 这里的overlaps似乎不是当前路径与之前搜索到的路径的重合度 而是一个用于选择截取哪个路径上的边的无实际含义的数
                olRatio = max(overlaps)
                maxOlIdx = overlaps.index(olRatio)
                if olRatio <= 0:
                    possible = False
                    break
                # Checking is finding a result is feasible
                # NotImplement

                overlap_edges = set(pathEdges_set[maxOlIdx].keys()) & set(path.edges)
                assert len(overlap_edges) > 0
                prioritized_edge = self.select([pathEdges_set[maxOlIdx][edge] for edge in overlap_edges])
                prioritized_edge.rank += 1
                self.graph.add_edge_cost(prioritized_edge.edge)
                # TODO find another stop flag
                # if len(pathEdges_list[maxOlIdx]) == 0:
                #     overlaps[maxOlIdx] = 0

                path = self.path_finding.search(
                    start, target, recorder)
                if path is None:
                    raise ValueError

                check = False

                success_idxes = []
                for idx, other_path in enumerate(resPaths):
                    new_overlap = self.compute_overlap(path, other_path)
                    overlaps[idx] = new_overlap
                    if new_overlap < overlap_theta:
                        success_idxes.append(idx)
                if len(success_idxes) < len(resPaths):
                    check = True

                # if len(success_idxes) == len(resPaths)-1:
                #     fail_index = len(resPaths)-1
                #     for x,y in zip(success_idxes,range(len(resPaths)-1)):
                #         if x!=y:
                #             fail_index = y
                #             break
                #     _, (a,b) = self.compute_overlap_specifically(path, resPaths[fail_index])
                #     if a<overlap_theta and b>=overlap_theta:
                #         del resPaths[fail_index]
                #         del pathEdges_set[fail_index]
                #         del overlaps[fail_index]
                #         resPaths.append(path)
                #         idx = len(resPaths)-1
                #         self.graph.ex_cost_unit  = path.time_info[-1]*(1+UNIT_RATIO)
                #         self.graph.add_node_constrain(nodes = set(path.nodes[1:-2]), constrain_unit = path.time_info[-1]*UNIT_RATIO/len(path.nodes))
                #         pathEdges_set.append(dict())
                #         overlaps.append(1)
                #         for edgeID in path.edges:
                #             pathEdges_set[idx][edgeID]=Prioritized_Edge(
                #                 priority=self.compute_priority(edgeID), edge=edgeID, idx=idx)
                #         print("**"*50)

                ###
                if not check:
                    print(overlaps)
                    resPaths.append(path)
                    print(len(resPaths))
                    idx = len(resPaths)-1
                    self.graph.ex_cost_unit  = path.time_info[-1]*(1+UNIT_RATIO)
                    self.graph.add_node_constrain(nodes = set(path.nodes[1:-2]), constrain_unit = path.time_info[-1]*UNIT_RATIO/len(path.nodes))
                    pathEdges_set.append(dict())
                    overlaps.append(1)
                    for edgeID in path.edges:
                        pathEdges_set[idx][edgeID]=Prioritized_Edge(
                            priority=self.compute_priority(edgeID), edge=edgeID, idx=idx)
                    #sort by path length
                    # num_result = len(resPaths)
                    # resPaths, pathEdges_set, overlaps = map(list, zip(*sorted(zip(resPaths, pathEdges_set[:num_result], overlaps[:num_result]), key=lambda items:self.graph._getPathLen(items[0].edges))))
                    
                    #
                    break

        return resPaths

class esx_re(esx_base):

    def search(self, start, target, k=10, overlap_theta=0.1, init_state=None, recorder=None):
        if init_state is None:
            resPaths = []

            path = self.path_finding.search(
                start, target, recorder)
            assert path is not None, "start:{} target:{} ".format(start, target)
            resPaths.append(path)

            if k == 1:
                return resPaths
        else:
            resPaths = init_state
        assert len(resPaths)<k
        pathEdges_set = [dict() for _ in range(len(resPaths))]

        for idx, path in enumerate(resPaths):
            for edgeID in path.edges:
                pathEdges_set[idx][edgeID] = Prioritized_Edge(
                    priority=self.compute_priority(edgeID), edge=edgeID, idx=idx)

        # overlaps 当前路径与之前搜索到的路径的重合度
        overlaps = [1]*len(resPaths)
        possible = True

        self.graph.ex_cost_unit  = path.time_info[-1]*(1+UNIT_RATIO)
        self.graph.set_node_constrain(nodes = set(path.nodes[1:-2]), constrain_unit = path.time_info[-1]*UNIT_RATIO/len(path.nodes))

        path = self.path_finding.search(
                start, target, recorder)
        if path is None:
            raise ValueError
        check = False
        success_idxes = []
        for idx, other_path in enumerate(resPaths):
            new_overlap = self.compute_overlap(path, other_path)
            overlaps[idx] = new_overlap
            if new_overlap < overlap_theta:
                success_idxes.append(idx)
        if len(success_idxes) < len(resPaths):
            check = True
        if not check:
            print(overlaps)
            resPaths.append(path)
            print(len(resPaths))
            idx = len(resPaths)-1
            self.graph.ex_cost_unit  = path.time_info[-1]*(1+UNIT_RATIO)
            self.graph.add_node_constrain(nodes = set(path.nodes[1:-2]), constrain_unit = path.time_info[-1]*UNIT_RATIO/len(path.nodes))
            pathEdges_set.append(dict())
            overlaps.append(1)
            for edgeID in path.edges:
                pathEdges_set[idx][edgeID]=Prioritized_Edge(
                    priority=self.compute_priority(edgeID), edge=edgeID, idx=idx)

        while (len(resPaths) < k and possible):
            iter_num = 0
            olRatio = 1

            # record below
            if recorder is not None:
                recorder.logger.info(
                    "new path : {}".format(pformat(resPaths[-1])))
                recorder.logger.info("overlaps : {}".format(overlaps))

            # record above

            while olRatio > overlap_theta:
                iter_num += 1
                if iter_num > MAX_ITER:
                    print("search fail")
                    return resPaths
                # 找到当前路径与哪个路径重合度最高 这里的overlaps似乎不是当前路径与之前搜索到的路径的重合度 而是一个用于选择截取哪个路径上的边的无实际含义的数
                olRatio = max(overlaps)
                maxOlIdx = overlaps.index(olRatio)
                if olRatio <= 0:
                    possible = False
                    break
                # Checking is finding a result is feasible
                # NotImplement

                overlap_edges = set(pathEdges_set[maxOlIdx].keys()) & set(path.edges)
                assert len(overlap_edges) > 0
                prioritized_edge = self.select([pathEdges_set[maxOlIdx][edge] for edge in overlap_edges])
                prioritized_edge.rank += 1
                self.graph.add_edge_cost(prioritized_edge.edge)
                # TODO find another stop flag
                # if len(pathEdges_list[maxOlIdx]) == 0:
                #     overlaps[maxOlIdx] = 0

                path = self.path_finding.search(
                    start, target, recorder)
                if path is None:
                    raise ValueError

                check = False

                success_idxes = []
                for idx, other_path in enumerate(resPaths):
                    new_overlap = self.compute_overlap(path, other_path)
                    overlaps[idx] = new_overlap
                    if new_overlap < overlap_theta:
                        success_idxes.append(idx)
                if len(success_idxes) < len(resPaths):
                    check = True

                ###
                if not check:
                    print(overlaps)
                    resPaths.append(path)
                    print(len(resPaths))
                    idx = len(resPaths)-1
                    self.graph.ex_cost_unit  = path.time_info[-1]*(1+UNIT_RATIO)
                    self.graph.add_node_constrain(nodes = set(path.nodes[1:-2]), constrain_unit = path.time_info[-1]*UNIT_RATIO/len(path.nodes))
                    pathEdges_set.append(dict())
                    overlaps.append(1)
                    for edgeID in path.edges:
                        pathEdges_set[idx][edgeID]=Prioritized_Edge(
                            priority=self.compute_priority(edgeID), edge=edgeID, idx=idx)
                    #sort by path length
                    # num_result = len(resPaths)
                    # resPaths, pathEdges_set, overlaps = map(list, zip(*sorted(zip(resPaths, pathEdges_set[:num_result], overlaps[:num_result]), key=lambda items:self.graph._getPathLen(items[0].edges))))
                    
                    #
                    break

        return resPaths