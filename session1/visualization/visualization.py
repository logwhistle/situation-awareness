import json
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap


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


def draw_map_conj():
    with open(r"E:\态势感知\other\map\real.gr", 'r') as f:
        adj_info = list(map(lambda args: (int(args[0]), int(args[1])),
                            [line.strip().split(" ") for line in f.readlines()]))
    with open(r"E:\态势感知\other\map\Points.co", 'r') as f:
        node_info = {node: (lo, la) for node, la, lo in (map(
            lambda args: (int(args[0]), float(args[1]), float(args[2])),
            [line.strip().split(" ") for line in f.readlines()]))}
    import numpy as np
    cors = np.array(list(node_info.values()))
    min_lo, min_la = np.min(cors, axis=0)
    max_lo, max_la = np.max(cors, axis=0)
    m = Basemap(llcrnrlon=min_lo, llcrnrlat=min_la,
                urcrnrlon=max_lo, urcrnrlat=max_la)

    for node_1, node_2 in adj_info:
        lo_1, la_1 = node_info[node_1]
        lo_2, la_2 = node_info[node_2]
        m.plot((lo_1, lo_2), (la_1, la_2), c="blue", latlon=True)

    bad_node = []
    # bad_node_set = set([591, 592, 593, 594,37, 74, 147, 198, 234, 252, 324, 333, 382, 385, 571, 675, 690, 700, 721, 748, 754, 755,738, 739,757, 758,679, 680,727, 728])
    for nodeID in node_info.keys():
        # if nodeID in bad_node_set:
        #     continue
        lo, la = node_info[nodeID]
        m.scatter(lo, la, latlon=True, c="red", marker="o", s=25)
        plt.annotate(str(nodeID), xy=(lo, la))
    for nodes in bad_node:
        los = []
        las = []
        for nodeID in nodes:
            lo, la = node_info[nodeID]
            los.append(lo)
            las.append(la)
        m.scatter(los, las, latlon=True, c="green", marker="o", s=25)

    plt.show()


def draw_map(paths=None, show_nodes=False, disabled_edges=None, untouchableEdges=None):
    with open(r"E:\态势感知\other\map\real.gr", 'r') as f:
        adj_info = list(map(lambda args: (int(args[0]), int(args[1])),
                            [line.strip().split(" ") for line in f.readlines()]))
    with open(r"E:\态势感知\other\map\Points.co", 'r') as f:
        node_info = {node: (lo, la) for node, la, lo in (map(
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
            np.linspace(1, 255, 1 + 2 + len(paths)).astype(np.int))
    else:
        color_list = ["blue"]
    plt.subplot(1, 2, 1)
    for node_1, node_2 in adj_info:
        i += 1
        lo_1, la_1 = node_info[node_1]
        lo_2, la_2 = node_info[node_2]
        m.plot((lo_1, lo_2), (la_1, la_2), c=color_list[0], latlon=True)
    plt.subplot(1, 2, 1)
    for node_1, node_2 in adj_info:
        i += 1
        lo_1, la_1 = node_info[node_1]
        lo_2, la_2 = node_info[node_2]
        m.plot((lo_1, lo_2), (la_1, la_2), c="blue", latlon=True)
    if show_nodes:
        for nodeID in node_info.keys():
            lo, la = node_info[nodeID]
            m.scatter(lo, la,
                      latlon=True, c="red", marker="o", s=25)
    plt.subplot(1, 2, 1)

    if paths is not None:
        start = paths[0].nodes[0]
        target = paths[0].nodes[-1]
        plt.subplot(1, 2, 2)
        m.scatter(node_info[start][0], node_info[start][1],
                  latlon=True, c=color_list[1], marker="o", s=200)
        m.scatter(node_info[target][0], node_info[target][1],
                  latlon=True, c=color_list[2], marker="*", s=200)
        plt.subplot(1, 2, 1)
        m.scatter(node_info[start][0], node_info[start][1],
                  latlon=True, c=color_list[1], marker="o", s=200)
        m.scatter(node_info[target][0], node_info[target][1],
                  latlon=True, c=color_list[2], marker="*", s=200)

        for color, path in zip(color_list[3:], paths):
            lots = []
            lats = []
            for node in path.nodes:
                lo, la = node_info[node]
                lots.append(lo)
                lats.append(la)
            m.plot(lots, lats, latlon=True, c=color)
    plt.subplot(1, 2, 2)
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

    plt.show()


if __name__ == "__main__":
    draw_map_conj()
