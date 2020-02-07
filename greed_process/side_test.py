import numpy as np
from sklearn.cluster import KMeans

X = np.array([[1, 2, 3, 3, 3], [1, 2, 3, 3, 3], [3, 3, 3, 2, 1], [10, 2, 2, 2, 2], [10, 4, 4, 4, 4], [10, 0, 2, 2, 2]])

kmeans = KMeans(n_clusters=4)
kmeans.fit(X)

centroids = kmeans.cluster_centers_
labels = kmeans.labels_

print(centroids)
print(labels)