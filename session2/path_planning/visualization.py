import json
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from mpl_toolkits.basemap import Basemap
import random
from copy import deepcopy
np.random.seed(123)
random.seed(123)

from k_means import KMeans


def draw_road():
    RoadLine_file = r"E:\态势感知\ronghuizhitong\Test_Exam\session\map\RoadLine.json"
    with open(RoadLine_file, "r", encoding="utf-8") as f:
        RoadLines = json.load(f)

    osm_0 = []
    for line in RoadLines:
        if line["properties"]["osm_id"] == 458:
            osm_0.append(line["geometry"]["coordinates"])
    assert len(osm_0) == 4
    min_lo, min_la = np.min(
        list(map(lambda x: np.min(x, axis=0), osm_0)), axis=0)
    max_lo, max_la = np.max(
        list(map(lambda x: np.max(x, axis=0), osm_0)), axis=0)
    m = Basemap(llcrnrlon=min_lo, llcrnrlat=min_la,
                urcrnrlon=max_lo, urcrnrlat=max_la)

    colors = ["red", "green", "blue", "black"]
    for i, line in enumerate(osm_0):
        for point in line:
            m.scatter(point[0], point[1], c=colors[i], latlon=True)
    plt.show()


def draw_map(paths=None, show_nodes = True, disabled_edges=None, untouchableEdges=None):
    with open(r"real.gr", 'r') as f:
        adj_info = list(map(lambda args: (int(args[0]), int(args[1])),
                        [line.strip().split(" ") for line in f.readlines()]))
    with open(r"Points.co", 'r') as f:
        node_info = {node: (lo, la) for node, lo, la in (map(
            lambda args: (int(args[0]), float(args[1]), float(args[2])),
            [line.strip().split(" ") for line in f.readlines()]))}
    import numpy as np
    cors = np.array(list(node_info.values()))
    min_lo, min_la = np.min(cors, axis=0)
    max_lo, max_la = np.max(cors, axis=0)
    m = Basemap(llcrnrlon=min_lo, llcrnrlat=min_la,
                urcrnrlon=max_lo, urcrnrlat=max_la)
    i = 0
    if paths is not None:
        color_list = plt.get_cmap("gist_ncar")(
            np.linspace(1, 255, 1+2+len(paths)).astype(np.int))
    else:
        color_list = ["blue"]
    plt.subplot(1,2,1)
    for node_1, node_2 in adj_info:
        i += 1
        lo_1, la_1 = node_info[node_1]
        lo_2, la_2 = node_info[node_2]
        m.plot((lo_1, lo_2), (la_1, la_2), c=color_list[0], latlon=True)
    plt.subplot(1,2,2)
    for node_1, node_2 in adj_info:
        i += 1
        lo_1, la_1 = node_info[node_1]
        lo_2, la_2 = node_info[node_2]
        m.plot((lo_1, lo_2), (la_1, la_2), c="blue", latlon=True)
    if show_nodes:
        for lo,la in node_info.values():
            m.scatter(lo, la,
                    latlon=True, c="red", marker="o", s=25)
    plt.subplot(1,2,1)

    if paths is not None:
        start = paths[0].nodes[0]
        target = paths[0].nodes[-1]
        plt.subplot(1,2,2)
        m.scatter(node_info[start][0], node_info[start][1],
                  latlon=True, c=color_list[1], marker="o", s=200)
        m.scatter(node_info[target][0], node_info[target][1],
                  latlon=True, c=color_list[2], marker="+", s=200)
        plt.subplot(1,2,1)
        m.scatter(node_info[start][0], node_info[start][1],
                  latlon=True, c=color_list[1], marker="o", s=200)
        m.scatter(node_info[target][0], node_info[target][1],
                  latlon=True, c=color_list[2], marker="+", s=200)

        for color, path in zip(color_list[3:], paths):
            lots = []
            lats = []
            for node in path.nodes:
                lo, la = node_info[node]
                lots.append(lo)
                lats.append(la)
            m.plot(lots, lats, latlon=True, c=color)
    plt.subplot(1,2,2)
    if disabled_edges is not None and untouchableEdges is not None:
        for edgeid in disabled_edges:
            lots = []
            lats = []
            for node in edgeid:
                lo, la = node_info[node]
                lots.append(lo)
                lats.append(la)
            m.plot(lots, lats, latlon=True, c="yellow")
        for edgeid in untouchableEdges:
            lots = []
            lats = []
            for node in edgeid:
                lo, la = node_info[node]
                lots.append(lo)
                lats.append(la)
            m.plot(lots, lats, latlon=True, c="red")
    plt.subplot(1,2,1)
    people = pd.read_table('people.txt', header=None)
    colors1 = '#00CED1' #点的颜色
    colors2 = '#DC143C'
    colors3 = '#FFF8DC'
    colors4 = '#D2691E'
    colors5 = '#000000'
    x, y = people.shape
    for i in range(x):
        if people.iloc[i, 1] == 1:
            plt.scatter(people.iloc[i,2], people.iloc[i,3], c=colors1, label='类别1')
        elif people.iloc[i, 1] == 2:
            plt.scatter(people.iloc[i, 2], people.iloc[i, 3], c=colors2, label='类别2')
        elif people.iloc[i, 1] == 3:
            plt.scatter(people.iloc[i, 2], people.iloc[i, 3], c=colors3, label='类别3')
        elif people.iloc[i, 1] == 4:
            plt.scatter(people.iloc[i, 2], people.iloc[i, 3], c=colors4, label='类别4')
        else:
            plt.scatter(people.iloc[i, 2], people.iloc[i, 3], c=colors5, label='类别5')
    # plt.show()

    X = people.iloc[:,[2,3]]
    y = people.iloc[:,1]
    y = y-1

    kmeans = KMeans(n_clusters=3)
    kmeans.fit(X.values, y.values)
    kmeans.plot_clusters(X.values)
    save = []
    x_data = deepcopy(X.values)

    for id_ in range(kmeans.k):
        points_idx = np.where(np.array(kmeans.new_assigns) == id_)[0]
        datapoints = x_data[points_idx]
        for j in range(3):
             centers = deepcopy(kmeans.centers)
             for i in range(25):
                dists = np.sqrt(np.sum((centers[id_] - datapoints)**2, axis=1))
                next_datapoint = datapoints[np.argmin(dists)]
                save.append(next_datapoint)
                centers[id_] = next_datapoint
                datapoints = np.delete(datapoints, np.argmin(dists), axis=0)

        # clist = plt.cm.get_cmap("rainbow")(np.linspace(0,255,3*3).astype(np.int))

    plt.subplot(1, 2, 1)
    for i in range(3*3):
        seg = np.array([kmeans.centers[i//3]] + save[i*25:(i+1)*25])
        plt.plot(seg[:,0],seg[:,1])
            # for j in range(25):
                # plt.scatter(*save[i*25+j],c = clist[i])
    #
    plt.show()

if __name__ == "__main__":
    draw_map()
