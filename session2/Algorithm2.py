# import json
# from operator import le
# import numpy as np
# import matplotlib.pyplot as plt
# import pandas as pd
# from mpl_toolkits.basemap import Basemap
# import random
# from copy import deepcopy
# from utils import PATH
# from session1.src.graph import BREAK_EVENT, graph_esx, ROADLINE
#
#
# np.random.seed(123)
# random.seed(123)
# import pickle
# from collections import defaultdict
# level_info = pickle.load(f)
# value_weights = np.array([-1, 1, 2, 3, 4, 5]).astype(np.float)
# dist_weights = np.array([-1, 7, 5, 1, 1, 1]) / 15
#
# from k_means import KMeans
# from shortest_path_finding import AStar
# from ESX import esx
# from graph import graph_static
#
#
#
# def parse_adj(dynamicMap):
#     edge = defaultdict(dict)
#     for segment in dynamicMap.segmentHashMap.values():
#         e1 = segment.endPoint1Id
#         e2 = segment.endPoint2Id
#         # 计算道路的通行时间，如果无法通行则返回-1
#         proirity = dynamicMap.getWeightOfSegment(e1, e2)
#         if len(segment.breakEventList) > 0:
#             breakEventList = []
#             for breakEventID in segment.breakEventList:
#                 breakEvent = dynamicMap.breakEventHashMap[breakEventID]
#                 break_speed = dynamicMap.getSpeedInBreakEvent(breakEvent)
#                 start_time = breakEvent.happendTime
#                 end_time = start_time + breakEvent.continueTime
#                 breakEventList.append(BREAK_EVENT(speed=break_speed, start_time=start_time, end_time=end_time))
#             assert len(breakEventList) == 1
#         else:
#             breakEventList = None
#         edge[e1][e2] = ROADLINE(length=segment.length, speed=segment.speed, proirity=proirity,
#                                 breakEventList=breakEventList)
#         edge[e2][e1] = ROADLINE(length=segment.length, speed=segment.speed, proirity=proirity,
#                                 breakEventList=breakEventList)
#     return edge
#
# def algorithm2(rescuePeopleTotal, map):
#     # plt.show()
#     levels = np.array(levels, dtype=np.int)
#     X = people
#     y = value_weights[levels]
#     kmeans = KMeans(n_clusters=3)
#     kmeans.fit(X, y)
#     kmeans.plot_clusters(X)
#     save = []
#     x_data = deepcopy(X)
#     dist_scale = dist_weights[levels]
#     for id_ in range(kmeans.k):
#         points_idx = np.where(np.array(kmeans.new_assigns) == id_)[0]
#         datapoints = x_data[points_idx]
#         datapoints_dist_scale = dist_scale[points_idx]
#         print(datapoints.shape)
#         for j in range(3):
#             centers = deepcopy(kmeans.centers)
#             for i in range(25):
#                 dists = datapoints_dist_scale * (np.sqrt(np.sum((centers[id_][:2] - datapoints[:, :2]) ** 2, axis=1)))
#                 min_index = np.argmin(dists)
#                 next_datapoint = datapoints[min_index]
#                 save.append(next_datapoint)
#                 centers[id_] = next_datapoint
#                 datapoints = np.delete(datapoints, min_index, axis=0)
#                 datapoints_dist_scale = np.delete(datapoints_dist_scale, min_index, axis=0)
#
#         # clist = plt.cm.get_cmap("rainbow")(np.linspace(0,255,3*3).astype(np.int))
#
#     graph = graph_static(adj_info)
#     path_finder = esx(graph)
#     plt.subplot(1, 2, 1)
#     paths = []
#     scores = []
#
#     plans = []
#     for i in range(3 * 3):
#         seg = np.array([kmeans.centers[i // 3]] + save[i * 25:(i + 1) * 25])
#         plans.append(seg[:, 2].astype(np.int).tolist())
#     paths = path_finder.search(plans)
#
#     for i in range(3 * 3):
#         seg = np.array([kmeans.centers[i // 3]] + save[i * 25:(i + 1) * 25])
#         plt.subplot(1, 2, 2)
#         plt.plot(seg[:, 0], seg[:, 1], marker="o", label=str(i))
#         plt.subplot(1, 2, 1)
#         path = paths[i]
#         path = path.top(25)
#         scores.append(compute_score(map(lambda personID: level_info[personID], path.people)))
#         X_cor, Y_cor = [], []
#         for node in path.nodes:
#             x, y = node_info[node]
#             X_cor.append(x)
#             Y_cor.append(y)
#         ln, = plt.plot(X_cor, Y_cor, label=str(i))
#         ln.set_lw(5)
#         ex_people = set(seg[:, 2].astype(np.int).tolist())
#         ac_people = set(path.people[:25])
#         saved_people = ex_people and ac_people
#         print("have searched {} people: {}".format(len(saved_people), saved_people))
#
#     from collections import Counter
#     print("*" * 20)
#     for path in paths:
#         people_levels = []
#         for people_id in path.people:
#             people_levels.append(level_info[people_id])
#         print(Counter(people_levels))
#     matrix = np.diag([1.] * len(paths))
#     for i in range(len(paths)):
#         for j in range(i + 1, len(paths)):
#             overlap = graph.compute_overlap(paths[i], paths[j])
#             matrix[i, j] = overlap
#             matrix[j, i] = overlap
#     print(matrix)
#     print(scores)
