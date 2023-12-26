from sklearn.cluster import KMeans
import numpy as np
import collections


# f = open(r'C:\Users\log_w\Desktop\points.txt', 'r')
# points_list = list(f)
#
# points, tmp, data = [], [], []
# left, right = 2, 4
# for i in range(1, len(points_list[0])-2):
#     point_list = points_list[0][i]
#     if point_list == '[':
#         data, tmp = [], []
#     elif point_list == ',':
#         d = ''.join(data)
#         tmp.append(float(d))
#         data = []
#     elif point_list == ']':
#         d = ''.join(data)
#         tmp.append(float(d))
#         points.append(tmp)
#     else:
#         data.append(point_list)
#
# X = np.array(points)

class Cluster:
    def __init__(self, X, n_clusters):
        self.X = np.array(X)
        self.n_clusters = n_clusters
        self.model = KMeans(n_clusters=self.n_clusters, random_state=0).fit(self.X)
        self.count = collections.Counter(self.model.labels_)

    def predict(self, point1Coordinate, point2Coordinate):
        proirity1 = 200 / self.count[self.model.predict([point1Coordinate])[0]]
        proirity2 = 200 / self.count[self.model.predict([point2Coordinate])[0]]
        return (proirity1 + proirity2) / 2

# #kmeans
# kmeans = KMeans(n_clusters=4, random_state=0).fit(X)
# print(kmeans.labels_)
# count = collections.Counter(kmeans.labels_)
# print(count)
# print(350/count[kmeans.predict([[12, 3]])[0]])
# # print(1/count[kmeans.predict([[12, 3]][0])])
# kmeans.predict([[0, 0], [12, 3]])
# print(kmeans.cluster_centers_)

# #MiniBatchKMeans
# from sklearn.cluster import MiniBatchKMeans
# # X = np.array([[1, 2], [1, 4], [1, 0], [4, 2], [4, 0], [4, 4], [4, 5], [0, 1], [2, 2], [3, 2], [5, 5], [1, -1]])
# # 手动配合批次
# kmeans = MiniBatchKMeans(n_clusters=4, random_state=0, batch_size=6)
# kmeans = kmeans.partial_fit(X[0:6,:])
# kmeans = kmeans.partial_fit(X[6:12,:])
# print(kmeans.cluster_centers_)
# kmeans.predict([[0, 0], [4, 4]])
# # 使用全部数据训练
# kmeans = MiniBatchKMeans(n_clusters=4, random_state=0, batch_size=6, max_iter=10).fit(X)
# print(kmeans.cluster_centers_)
# kmeans.predict([[0, 0], [4, 4]])
#
#
# #mean shift
# from sklearn.cluster import MeanShift
# clustering = MeanShift(bandwidth=1).fit(X)  #Bandwidth used in the RBF kernel, bigger,smaller
# print(clustering.labels_)
# clustering.predict([[0, 0], [5, 5]])
# print(clustering)
# # MeanShift(bandwidth=2)
