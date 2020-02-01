from scipy import spatial
import numpy as np
a = np.array([2.0,1.0])
b = np.array([5.0,3.0])
dis = 1 - spatial.distance.cosine(a,b)
#----------------------
# 0.99705448550158149
#----------------------
c = np.array([5.0,4.0])
dis2 = 1 - spatial.distance.cosine(c,b)
#----------------------
# 0.99099243041032326
#----------------------

mean_ab = sum(sum(a,b)) / 4
print(sum(a,b))
print(mean_ab)