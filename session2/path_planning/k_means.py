import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import random
from sklearn.datasets import make_blobs
from copy import deepcopy
np.random.seed(123)
random.seed(123)

# X, y = make_blobs(centers=5, n_samples=500)
# np.random.shuffle(y)
# print(f'Shape of dataset: {X.shape}')
# # fig = plt.figure(figsize=(8,6))
# # plt.scatter(X[:,0], X[:,1], c=y)
# # plt.title("Dataset with 5 clusters")
# # plt.xlabel("First feature")
# # plt.ylabel("Second feature")
# plt.show()
# W = np.array([-1, 5/15, 4/15, 3/15, 2/15, 1/15])
# weights = W[y]

class KMeans():
    def __init__(self, n_clusters=4):
        self.k = n_clusters
    def fit(self, data, y):
        """
        Fits the k-means model to the given dataset
        """
        n_samples, _ = data.shape
        # initialize cluster centers
        self.centers = np.array(random.sample(list(data), self.k)) #随便找3个起始点
        print(list(data))
        self.initial_centers = np.copy(self.centers)
# We will keep track of whether the assignment of data points
# to the clusters has changed. If it stops changing, we are
# done fitting the model
        old_assigns = None
        n_iters = 0
        while True:
            # print(n_iters)
            new_assigns = [self.classify(datapoint, weight) for datapoint, weight in zip(data, y)]

            if new_assigns == old_assigns:
                print(f"Training finished after {n_iters} iterations!")
                self.new_assigns = new_assigns
                
                dummy_center = []
                for center in self.centers:
                    dists = np.sqrt(np.sum((center[:2] - data[:,:2])**2, axis=1))
                    index = np.argmin(dists)
                    dummy_center.append(data[index])
                self.centers = np.array(dummy_center)
                return
            old_assigns = new_assigns

            n_iters += 1
        # recalculate centers
            for id_ in range(self.k):
                points_idx = np.where(np.array(new_assigns) == id_)
                datapoints = data[points_idx]
                self.centers[id_] = datapoints.mean(axis=0)
        self.new_assigns = new_assigns
        print('run')
    def l2_distance(self, datapoint, weight):
        dists = weight * np.sqrt(np.sum((self.centers[:,:2] - datapoint[:2])**2, axis=1))
        return dists

    def classify(self, datapoint, weight):
        dists = self.l2_distance(datapoint, weight)
        return np.argmin(dists)  #argmin找出水平方向最小值的下标

    def plot_clusters(self, data):
        # plt.figure(figsize=(12,10))
        plt.title("Centers green v")
    #    plt.scatter(data[:, 0], data[:, 1], marker='.', c=y)
        plt.scatter(self.centers[:, 0], self.centers[:,1], c='green',marker='v',s=300)
    #   plt.scatter(self.initial_centers[:, 0], self.initial_centers[:,1], c='k')

if __name__=="__main__":

    kmeans = KMeans(n_clusters=3)

    kmeans.fit(X, y)

    kmeans.plot_clusters(X)

    save = []

    x_data = deepcopy(X)

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


    for i in range(3*3):
        seg = np.array([kmeans.centers[i//3]] + save[i*25:(i+1)*25])
        plt.plot(seg[:,0],seg[:,1])
        # for j in range(25):
            # plt.scatter(*save[i*25+j],c = clist[i])
    #
    plt.show()

