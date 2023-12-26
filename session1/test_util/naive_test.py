from copy import deepcopy
import pickle
from collections import defaultdict
from functools import reduce
import numpy as np
import tqdm
import random 
from math import ceil
random.seed(233)

from maps.StaticMap import StaticMap
from session1.KSPWLO import parse_adj
from session1.src.graph import graph_static
from session1.src.ESX import esx

def tester(kspf):
    with open("session1/test_util/test_data.pickle","rb") as f:
        tasks = pickle.load(f)
    tasks = reduce(lambda x,y:x+y , tasks.values())
    random.shuffle(tasks)

    K = 10
    overlap_theta = 0.1
    meta_info = {
                    "K":K,
                    "overlap_theta":overlap_theta,
                }

    result = test_core(kspf, tasks, meta_info, tqdm_show=True)
    global_mean = np.mean(reduce(lambda x,y:x+y , result.values()))
    print(global_mean)
    record = [[k,np.mean(result[k])] for k in result.keys()]
    record.sort(key= lambda x:x[0])
    x,y = zip(*record)
    from matplotlib import pyplot as plt
    plt.plot(x,y)
    for x,y in record:
        plt.annotate("({}, {:.2f})".format(x,y), xy=(x,y),xytext=(-1, 1), textcoords='offset points', color='red')
    plt.show()

def multi_tester(parsedGraph, num_process = 30):
    import multiprocessing as mp
    with open("session1/test_util/test_data.pickle","rb") as f:
        tasks = pickle.load(f)
    T = []
    for num in tasks.keys():
        T+=np.concatenate([np.array(tasks[num], dtype=np.int), np.array([num]*len(tasks[num]), dtype=np.int)[:,np.newaxis]], axis=1).tolist()

    tasks = T
    # tasks = reduce(lambda x,y:x+y , tasks.values())
    random.shuffle(tasks)
    # tasks = tasks[:100]
    K = 10
    overlap_theta = 0.1
    meta_info = {
                    "K":K,
                    "overlap_theta":overlap_theta,
                    "parsedGraph":parsedGraph,
                }

    pool = mp.Pool(num_process)
    slide_size = ceil(len(tasks)/num_process)
    works = [pool.apply_async(test_core, args=(tasks[i*slide_size:(i+1)*slide_size], meta_info), kwds={"tqdm_show": i==0}) for i in range(num_process)]
    results = [work.get() for work in works]
    pool.close()
    keys = set()
    for raw_result in results:
        keys |= set(raw_result.keys())
    result = dict()
    for num in keys:
        temp = []
        for raw_result in results:
            if num in raw_result:
                temp += raw_result.get(num)
        result[num] = temp

    global_mean = np.mean(reduce(lambda x,y:x+y , result.values()))
    print(global_mean)
    record = [[k,np.mean(result[k])] for k in result.keys()]
    record.sort(key= lambda x:x[0])
    x,y = zip(*record)
    from matplotlib import pyplot as plt

    fig = plt.figure(figsize=(16,9))
    ax = fig.add_axes([0.1,0.1,0.8,0.8])
    ax.plot(x,y)
    for x,y in record:
        ax.annotate("({}, {:.2f})".format(x,y), xy=(x,y),xytext=(-1, 1), textcoords='offset points', color='red')
    
    # plt.savefig("PIC/image.png",dpi = 160)
    plt.show()

def test_core(task, meta_info, tqdm_show = False):
    parsedGraph = meta_info["parsedGraph"]
    graph = graph_static(parsedGraph)
    kspf = esx(graph)
    kspf = deepcopy(kspf)
    graph = kspf.graph
    K = meta_info["K"]
    overlap_theta = meta_info["overlap_theta"]

    result = defaultdict(list)

    if tqdm_show:
        task = tqdm.tqdm(task)
    for start, target, num in task:
        graph.reset()
        paths = kspf.search(start, target, K, overlap_theta)
        assert len(paths)>0
        result[num].append(len(paths))
    return result


if __name__=="__main__":
    
    
    rootAddress = "originalFile\\"
    # 建立静态地图
    staticMap = StaticMap(rootAddress)
    
    parsedGraph = {"parsed_adj": parse_adj(staticMap)}


    multi_tester(parsedGraph)