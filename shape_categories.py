import numpy as np
from scipy.spatial import distance_matrix
import shutil
import os

shape_set = 3
path_src = f'./shapes_{shape_set}/'
SC = np.loadtxt(path_src + 'SC.txt', dtype='f', delimiter=',')

D = distance_matrix(SC, SC)

N_stim, N_dims = SC.shape
N_categories = 2
N_diff_levels = 5

cat_bounds = np.linspace(0, N_stim, N_categories + 1, dtype='i') 
cat_ranges = np.empty(N_categories, dtype=np.ndarray)
for i in range(0, N_categories):
    cat_ranges[i] = np.arange(cat_bounds[i], cat_bounds[i+1])

avg_dists = np.zeros(N_stim)
for i in range(0, N_stim):
    other_cats = [r for r in cat_ranges if i not in r]
    avg_dists[i] = np.mean(D[i, other_cats])

diffs = np.zeros(N_stim, dtype='i')
c = 0
for r in cat_ranges:
    cat_avgd = avg_dists[r]
    idxs = cat_avgd.argsort()[::-1] # sort by maximum average distance across other categories 
    idxs_diff = np.array_split(idxs, N_diff_levels)
    for j, dj in enumerate(idxs_diff):
        diffs[dj + c] = j
    c += len(r)    

path_dest = f'./stimuli/pack_shapes_{shape_set}/'

for i, r in enumerate(cat_ranges):
    for ex in r[::2]:
        dir_dest = path_dest + f'cat_{i+1}/' + f'diff_{diffs[ex]+1}/'
        os.makedirs(dir_dest, exist_ok=True)
        c = len(os.listdir(dir_dest))

        file_src = path_src + f'shape_{ex+1}.png'
        file_dest =  dir_dest + f'ex_{i+1}_{diffs[ex]+1}_{c+1}.png'
        shutil.copy(file_src, file_dest)



