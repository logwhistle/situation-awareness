from maps.StaticMap import StaticMap
from session1.KSPWLO import parse_adj
from session1.src.graph import graph_static
from session1.src.shortest_path_finding import AStar
TEST = True

from random import sample
from collections import defaultdict
import tqdm

def sample_task(nodes, old_tasks):
    max_iter = 10000
    i = 0
    while True:
        if i>=max_iter:
            raise RuntimeError
        start, target = sample(nodes, 2)
        if not (start, target) in old_tasks:
            return start, target
    

if __name__ == "__main__":
    # 预处理阶段
    # 根目录
    rootAddress = "originalFile\\"
    # 建立静态地图
    staticMap = StaticMap(rootAddress)
    
    parsedGraph = {"parsed_adj": parse_adj(staticMap)}
    graph = graph_static(parsedGraph)
    nodes = list(graph.edge.keys())
    bad_nodes = [438, 439]
    for node in bad_nodes:
        nodes.remove(node)
    path_finder = AStar(graph)

    N = 10000
    min_path_len = 10

    old_tasks = set()
    tasks = defaultdict(list)
    num_tasks = 0
    with tqdm.tqdm(total=N) as pbar:
        iter = 1
        max_iter = 10*N
        while True:
            start, target = sample_task(nodes, old_tasks)
            old_tasks.add((start, target))
            path = path_finder.search(start, target)
            assert path is not None
            if len(path.edges)<min_path_len:
                continue
            tasks[len(path.edges)].append((start, target))
            num_tasks+=1
            if iter>=N or iter>=max_iter:
                break
            iter+=1
            pbar.update(1)
    
    print(num_tasks)
    record = [(k,len(tasks[k])) for k in tasks.keys()]
    record.sort(key= lambda x:x[0])
    x,y = zip(*record)
    from matplotlib import pyplot as plt
    plt.plot(x,y)
    plt.show()

    import pickle
    with open("session1/test_util/test_data.pickle","wb") as f:
        pickle.dump(tasks, f)

    # if TEST:
    #     # 测试静态图
    #     testOfStatic = TestOfRes(sbj=None, res=None, map=staticMap, roadLineListList=None, segmentListList=None,
    #                              pointIdListList=None, isolatedPoint=staticMap.res)

    # # session1project1调用50次
    # time = 6
    # report_list = []
    # for sendId in range(1, time):
    #     print("\n===================================== 科目一/情景一 开始运行client_path_" + str(
    #         sendId) + " =====================================")
    #     rootAddress = "originalFile\\"
    #     session1sbj1 = Session1Sbj1(rootAddress=rootAddress, FileNumber=sendId, staticMap=staticMap, BreakInfo=breakInfo)
    #     res = session1sbj1.finalRes
    #     if TEST:
    #         if sendId < time:
    #             roadLine = None
    #             Segment = None
    #             roadPoint = None  # [[]]
    #
    #             testOfsession1Sbj1 = TestOfRes(sbj=session1sbj1, map=None, res=res, roadLineListList=roadLine,
    #                                            segmentListList=Segment, pointIdListList=roadPoint, isolatedPoint=None)
    #     report_list.append(len(res))
    # print("session1:\t paths_num:{} \n\t average_num:{}".format(report_list, sum(report_list) / len(report_list)))


    # input("\n\n按下 enter 键后退出。")


