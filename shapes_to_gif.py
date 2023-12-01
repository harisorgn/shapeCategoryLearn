import numpy as np
from scipy.spatial import distance_matrix
import shutil
import os

from utils import *

shape_set = 1
path_src = f'./shapes_{shape_set}/'
SC = np.loadtxt(path_src + 'SC.txt', dtype='f', delimiter=',')
D = distance_matrix(SC, SC)

N_categories = 2
N_stim = SC.shape[0]

diffs = split_diff(SC, N_categories)
cat_ranges = category_ranges(N_stim, N_categories)

path_dest = f'./stimuli/pack_shapes_{shape_set}/'

avg_dists = avg_dist_to_other_categories(D, cat_ranges)

prototype_IDs = category_prototypes(D, cat_ranges)

p = prototype_IDs[0]+1
s = cat_ranges[0][-1]+1

write_shape_gif(s, p, path_src)