import numpy as np
from sklearn.cluster import KMeans
from general.tools import load_data
#
# X = np.array([[1, 2, 3, 3, 3], [1, 2, 3, 3, 3], [3, 3, 3, 2, 1], [10, 2, 2, 2, 2], [10, 4, 4, 4, 4], [10, 0, 2, 2, 2]])
#
# kmeans = KMeans(n_clusters=4)
# kmeans.fit(X)
#
# centroids = kmeans.cluster_centers_
# labels = kmeans.labels_0
#
# print(centroids)
# print(labels)

path_cluster_group_data = "../statistics_collection/data"
movies_plot = load_data(path_cluster_group_data, 'movie_plot')
movie_plot = movies_plot[118]
movie_plot.down_sample_strict(n=10)


pass