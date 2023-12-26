import json
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
from copy import deepcopy
from session2.path_planning.k_means import KMeans
from session2.path_planning.ESX import esx
from session2.path_planning.graph import graph_static


def draw_road():
    RoadLine_file = r"..\other\map\RoadLine.json"
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


def compute_score(levels):
    score = 0
    for level in levels:
        score += value_weights[level]
    return score

def assign_task(dynamicMap, plot_flag=False):
    value_weights = np.array([-1, 1, 2, 3, 4, 5, 1]).astype(np.float)
    dist_weights = np.array([-1, 7, 5, 1, 1, 1]) / 15

    levels = []
    X = [] #people cor
    w = [] #weight for people
    for pointId, peopleIdList in dynamicMap.peopleIndexHashMap.items():
        point = dynamicMap.roadPointHashMap[pointId]
        for peopleId in peopleIdList:
            people = dynamicMap.peopleHashMap[peopleId]
            x = [point.getLongitude(), point.getLatitude(), pointId]
            X.append(x)
            levels.append(people.type)
    levels = np.array(levels, dtype=np.int)
    X = np.array(X, dtype=np.float)
    w = value_weights[levels]
    kmeans = KMeans(n_clusters=3)
    kmeans.fit(X, w)
    save = []
    x_data = deepcopy(X)
    dist_scale = dist_weights[levels]

    for id_ in range(kmeans.k):
        points_idx = np.where(np.array(kmeans.new_assigns) == id_)[0]
        datapoints = x_data[points_idx]
        datapoints_dist_scale = dist_scale[points_idx]
        print(datapoints.shape)
        for j in range(3):
            centers = deepcopy(kmeans.centers)
            for i in range(25):
                dists = datapoints_dist_scale * (np.sqrt(np.sum((centers[id_][:2] - datapoints[:, :2]) ** 2, axis=1)))
                min_index = np.argmin(dists)
                next_datapoint = datapoints[min_index]
                save.append(next_datapoint)
                centers[id_] = next_datapoint
                datapoints = np.delete(datapoints, min_index, axis=0)
                datapoints_dist_scale = np.delete(datapoints_dist_scale, min_index, axis=0)

    plans = []
    for i in range(3 * 3):
        seg = np.array([kmeans.centers[i // 3]] + save[i * 25:(i + 1) * 25])
        plans.append(seg[:, 2].astype(np.int).tolist())
    if plot_flag:
        plt.subplot(1, 2, 2)
        for i in range(3 * 3):
            seg = np.array([kmeans.centers[i // 3]] + save[i * 25:(i + 1) * 25])
            plt.plot(seg[:, 0], seg[:, 1], marker="o", label=str(i))

    return plans

def search_path(plans):
    graph = graph_static(adj_info)
    path_finder = esx(graph)
    scores = []

    paths = path_finder.search(plans)
    for i in range(3 * 3):
        path = paths[i]
        path = path.top(25)
        # TODO
        scores.append(compute_score(map(lambda personID: level_info[personID], path.people)))
        X_cor, Y_cor = [], []
        for node in path.nodes:
            x, y = node_info[node]
            X_cor.append(x)
            Y_cor.append(y)
        ln, = plt.plot(X_cor, Y_cor, label=str(i))
        ln.set_lw(5)

    from collections import Counter
    print("*" * 20)
    for path in paths:
        people_levels = []
        for people_id in path.people:
            people_levels.append(level_info[people_id])
        print(Counter(people_levels))
    matrix = np.diag([1.] * len(paths))
    for i in range(len(paths)):
        for j in range(i + 1, len(paths)):
            overlap = graph.compute_overlap(paths[i], paths[j])
            matrix[i, j] = overlap
            matrix[j, i] = overlap
    print(matrix)
    print(scores)
    plt.legend()
    plt.show()



def draw_map(paths=None, show_nodes=False, disabled_edges=None, untouchableEdges=None):
    import numpy as np
    cors = np.array(list(node_info.values()))
    # 新建地图画布
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
    for node_1 in adj_info.keys():
        for node_2 in adj_info[node_1]:
            i += 1
            lo_1, la_1 = node_info[node_1]
            lo_2, la_2 = node_info[node_2]
            m.plot((lo_1, lo_2), (la_1, la_2), c=color_list[0], latlon=True)
    plt.subplot(1, 2, 2)
    for node_1 in adj_info.keys():
        for node_2 in adj_info[node_1]:
            i += 1
            lo_1, la_1 = node_info[node_1]
            lo_2, la_2 = node_info[node_2]
            m.plot((lo_1, lo_2), (la_1, la_2), c="blue", latlon=True)
    if show_nodes:
        for lo, la in node_info.values():
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
                  latlon=True, c=color_list[2], marker="+", s=200)
        plt.subplot(1, 2, 1)
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
    plt.subplot(1, 2, 1)
    people = []
    for node in node_info.keys():
        if node >= 10000:
            people.append(list(node_info[node]) + [node])
    people = np.array(people)
    print(people.shape)
    colors1 = '#00CED1'  # 点的颜色
    colors2 = '#DC143C'
    colors3 = '#FFF8DC'
    colors4 = '#D2691E'
    colors5 = '#000000'

    levels = []

    for i in range(10000, 10499):
        levels.append(level_info[i])
        if level_info[i] == 1:
            plt.scatter(people[i - 10000, 0], people[i - 10000, 1], c=colors1)
        elif level_info[i] == 2:
            plt.scatter(people[i - 10000, 0], people[i - 10000, 1], c=colors2)
        elif level_info[i] == 3:
            plt.scatter(people[i - 10000, 0], people[i - 10000, 1], c=colors3)
        elif level_info[i] == 4:
            plt.scatter(people[i - 10000, 0], people[i - 10000, 1], c=colors4)
        else:
            plt.scatter(people[i - 10000, 0], people[i - 10000, 1], c=colors5)

    # plt.show()
    levels = np.array(levels, dtype=np.int)
    X = people
    y = value_weights[levels]
    kmeans = KMeans(n_clusters=3)
    kmeans.fit(X, y)
    kmeans.plot_clusters(X)
    save = []
    x_data = deepcopy(X)
    dist_scale = dist_weights[levels]
    for id_ in range(kmeans.k):
        points_idx = np.where(np.array(kmeans.new_assigns) == id_)[0]
        datapoints = x_data[points_idx]
        datapoints_dist_scale = dist_scale[points_idx]
        print(datapoints.shape)
        for j in range(3):
            centers = deepcopy(kmeans.centers)
            for i in range(25):
                dists = datapoints_dist_scale * (np.sqrt(np.sum((centers[id_][:2] - datapoints[:, :2]) ** 2, axis=1)))
                min_index = np.argmin(dists)
                next_datapoint = datapoints[min_index]
                save.append(next_datapoint)
                centers[id_] = next_datapoint
                datapoints = np.delete(datapoints, min_index, axis=0)
                datapoints_dist_scale = np.delete(datapoints_dist_scale, min_index, axis=0)

        # clist = plt.cm.get_cmap("rainbow")(np.linspace(0,255,3*3).astype(np.int))

    graph = graph_static(adj_info)
    path_finder = esx(graph)
    plt.subplot(1, 2, 1)
    paths = []
    scores = []

    plans = []
    for i in range(3 * 3):
        seg = np.array([kmeans.centers[i // 3]] + save[i * 25:(i + 1) * 25])
        plans.append(seg[:, 2].astype(np.int).tolist())
    paths = path_finder.search(plans)

    for i in range(3 * 3):
        seg = np.array([kmeans.centers[i // 3]] + save[i * 25:(i + 1) * 25])
        plt.subplot(1, 2, 2)
        plt.plot(seg[:, 0], seg[:, 1], marker="o", label=str(i))
        plt.subplot(1, 2, 1)
        path = paths[i]
        path = path.top(25)
        scores.append(compute_score(map(lambda personID: level_info[personID], path.people)))
        X_cor, Y_cor = [], []
        for node in path.nodes:
            x, y = node_info[node]
            X_cor.append(x)
            Y_cor.append(y)
        ln, = plt.plot(X_cor, Y_cor, label=str(i))
        ln.set_lw(5)
        ex_people = set(seg[:, 2].astype(np.int).tolist())
        ac_people = set(path.people[:25])
        saved_people = ex_people and ac_people
        print("have searched {} people: {}".format(len(saved_people), saved_people))

    from collections import Counter
    print("*" * 20)
    for path in paths:
        people_levels = []
        for people_id in path.people:
            people_levels.append(level_info[people_id])
        print(Counter(people_levels))
    matrix = np.diag([1.] * len(paths))
    for i in range(len(paths)):
        for j in range(i + 1, len(paths)):
            overlap = graph.compute_overlap(paths[i], paths[j])
            matrix[i, j] = overlap
            matrix[j, i] = overlap
    print(matrix)
    print(scores)
    plt.legend()
    plt.show()


if __name__ == "__main__":
    draw_map()
