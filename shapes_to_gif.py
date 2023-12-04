import numpy as np
from scipy.spatial import distance_matrix

from utils import *

shape_set = 1
path_src = f'./shapes_{shape_set}/'
SC = np.loadtxt(path_src + 'SC.txt', dtype='f', delimiter=',')
D = distance_matrix(SC, SC)

N_categories = 2
N_stim = SC.shape[0]

diffs = split_diff(SC, N_categories)
cat_ranges = category_ranges(N_stim, N_categories)

path_dest = f'./stimuli/pack_morph_shapes_{shape_set}/'

prototype_IDs = category_prototypes(D, cat_ranges)

for i, r in enumerate(cat_ranges):
    prototype = prototype_IDs[i]
    for ex in r[::2]:
        shape_ID = ex + 1
        prototype_ID = prototype_IDs[i] + 1
        diff_level = diffs[ex] + 1
        category_ID = i + 1

        dir_dest = path_dest + f'cat_{category_ID}/' + f'diff_{diff_level}/'

        if shape_ID != prototype_ID :
            write_shape_gif(shape_ID, prototype_ID, diff_level, category_ID, path_src, dir_dest)
