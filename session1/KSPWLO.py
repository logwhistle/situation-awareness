import numpy as np
from collections import defaultdict
from session1.src.graph import BREAK_EVENT, graph_esx, ROADLINE
from session1.src.ESX import esx, esx_re


def parse_co(RoadPointInfo):
    raise NotImplementedError


def parse_adj(dynamicMap):
    edge = defaultdict(dict)
    for segment in dynamicMap.segmentHashMap.values():
        e1 = segment.endPoint1Id
        e2 = segment.endPoint2Id
        # 计算道路的通行时间，如果无法通行则返回-1
        proirity = dynamicMap.getWeightOfSegment(e1, e2)
        if len(segment.breakEventList) > 0:
            breakEventList = []
            for breakEventID in segment.breakEventList:
                breakEvent = dynamicMap.breakEventHashMap[breakEventID]
                break_speed = dynamicMap.getSpeedInBreakEvent(breakEvent)
                start_time = breakEvent.happendTime
                end_time = start_time + breakEvent.continueTime
                breakEventList.append(BREAK_EVENT(speed=break_speed, start_time=start_time, end_time=end_time))
            assert len(breakEventList) == 1
        else:
            breakEventList = None
        edge[e1][e2] = ROADLINE(length=segment.length, speed=segment.speed, proirity=proirity,
                                breakEventList=breakEventList)
        edge[e2][e1] = ROADLINE(length=segment.length, speed=segment.speed, proirity=proirity,
                                breakEventList=breakEventList)
    return edge


class KSPWLO_Searcher:
    def __init__(self, parsedGraph) -> None:
        self.graph = graph_esx(parsedGraph)
        self.kspf = esx(self.graph)

    def search(self, start, target, K=10, overlap_theta=0.1, init_state=None):
        self.graph.reset()
        paths = self.kspf.search(start, target, K, overlap_theta, init_state=init_state)
        numpath = len(paths)
        matrix = np.diag([1.] * numpath).astype(np.float)

        for i in range(numpath):
            for j in range(i + 1, numpath):
                overlap = self.graph.compute_overlap(paths[j], paths[i])[0]
                matrix[i, j] = overlap
                matrix[j, i] = overlap


        print(matrix)
        return paths
        # 需要安装basemap库才能画图
        # from visualization.visualization import draw_map
        # draw_map(paths,show_nodes=True)

    # def search_twice(self, paths, target, dynamic_time=0, K=1, overlap_theta=0.2):  # breaktime的时间
    #     # 情景二：在dynamic_time时间点出现动态信息后，更新动态新的地图作为self.graph_dynamic，在已有paths下重新寻找路径
    #     from session1.find_beg import find_begin
    #     new_paths, nodes = [], []
    #     # dynamic_time = 0
    #     begs = find_begin(dynamic_time, paths, self.graph)  # paths为已找到的所有最优路径
    #     results = begs.find()
    #     for i in range(0, len(results)):
    #         result = results[i]
    #         a0 = result[3] + self.kspf.search(result[0], target, K, overlap_theta)[i].time_info[-1]  # time of kspf.search()
    #         a1 = result[4] + self.kspf.search(result[1], target, K, overlap_theta)[i].time_info[-1]  # time of kspf.search()
    #         if a0 < a1:
    #             new_paths.append(self.kspf.search(result[0], target, 1, 0.5))
    #             node = result[0]
    #         else:
    #             new_paths.append(self.kspf.search(result[1], target, 1, 0.5))
    #             node = result[1]
    #         nodes.append([node, result[0], result[1], result[4]])  # [走的点， 端点1， 端点2， 距离端点1的距离]
    #     return new_paths, nodes

class KSPWLO_reSearcher:
    def __init__(self, parsedGraph) -> None:
        self.graph = graph_esx(parsedGraph)
        self.kspf = esx_re(self.graph)

    def search(self, start, target, K=10, overlap_theta=0.1, init_state=None):
        self.graph.reset()
        paths = self.kspf.search(start, target, K, overlap_theta, init_state=init_state)
        numpath = len(paths)
        matrix = np.diag([1.] * numpath).astype(np.float)

        for i in range(numpath):
            for j in range(i + 1, numpath):
                overlap = self.graph.compute_overlap(paths[j], paths[i])[0]
                matrix[i, j] = overlap
                matrix[j, i] = overlap


        print(matrix)
        return paths