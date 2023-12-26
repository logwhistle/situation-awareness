from session2.path_planning.shortest_path_finding import AStar

from session2.path_planning.utils import PATH, Prioritized_Edge, Init_State, Search_Node

MAX_ITER = 200
UNIT_RATIO = 1


class esx:
    def __init__(self, graph) -> None:
        self.graph = graph
        self.path_finding = AStar(graph)
        self.meta_info = {}

    def compute_overlap(self, path1, path2):
        return self.graph.compute_overlap(path1, path2)

    def compute_priority(self, edge_info):
        """
        Let starts be all the nodes which are the starting points of all incoming edges to the source of the given edge.
        Let Target be all the nodes which are the ending points of all outgoing edges from the target of the given edge.
        This function returns the number of shortest paths from some source to some target that contain the given edge.
        """
        e1, e2 = edge_info
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
        return priority  # 最大

    def search(self, tasks, overlap_theta=0.2, people_num=25, recorder=None):

        resPaths = []
        pathEdges_set = []
        overlaps = []

        def iter_task(task):
            for i in range(len(task) - 1):
                yield task[i:i + 2]

        for task in tasks:
            iter_num = 0
            olRatio = 1
            while True:
                iter_num += 1
                if iter_num > MAX_ITER:
                    print(overlaps)
                    resPaths.append(path)
                    print(len(resPaths))
                    idx = len(resPaths) - 1
                    pathEdges_set.append(dict())
                    overlaps.append(1)
                    for edgeID in path.edges:
                        pathEdges_set[idx][edgeID] = Prioritized_Edge(
                            priority=self.compute_priority(edgeID), edge=edgeID, idx=idx)
                    # sort by path length
                    num_result = len(resPaths)
                    resPaths, pathEdges_set, overlaps = map(list, zip(*sorted(
                        zip(resPaths, pathEdges_set[:num_result], overlaps[:num_result]),
                        key=lambda items: self.graph._getPathLen(items[0].edges))))

                    #
                    break
                path = PATH(None, None, None)
                for start, target in iter_task(task):

                    temp_path = self.path_finding.search(
                        start, target, recorder)
                    assert temp_path is not None, "start:{} target:{} ".format(start, target)
                    path += temp_path
                    if len(path.people) >= people_num:
                        break

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
                    idx = len(resPaths) - 1
                    pathEdges_set.append(dict())
                    overlaps.append(1)
                    for edgeID in path.edges:
                        pathEdges_set[idx][edgeID] = Prioritized_Edge(
                            priority=self.compute_priority(edgeID), edge=edgeID, idx=idx)

                    #
                    break
                else:
                    olRatio = max(overlaps)
                    maxOlIdx = overlaps.index(olRatio)
                    overlap_edges = set(pathEdges_set[maxOlIdx].keys()) & set(path.edges)
                    assert len(overlap_edges) > 0
                    prioritized_edge = max([pathEdges_set[maxOlIdx][edge] for edge in overlap_edges])
                    prioritized_edge.rank += 1
                    self.graph.add_edge_cost(prioritized_edge.edge)

        return resPaths
