import shutil
import os

import numpy as np
from scipy.spatial import distance_matrix
import imageio.v3 as iio
import imageio.v2 as iiov2
from pygifsicle import optimize

def category_ranges(N_stim, N_categories):
    cat_bounds = np.linspace(0, N_stim, N_categories + 1, dtype='i') 
    cat_ranges = np.empty(N_categories, dtype=np.ndarray)
    for i in range(0, N_categories):
        cat_ranges[i] = np.arange(cat_bounds[i], cat_bounds[i+1])
    
    return cat_ranges

def category_prototypes(D, cat_ranges):
    N_categories = len(cat_ranges)
    avg_dist = avg_dist_to_other_categories(D, cat_ranges)

    prototype_IDs = np.empty(N_categories, dtype=int)
    for i, r in enumerate(cat_ranges):
        idx = np.where(avg_dist == np.max(avg_dist[r]))[0]
        assert idx in r, f'Prototype appears to not belong to category {i}'
        prototype_IDs[i] = idx
    
    return prototype_IDs

def avg_dist_to_other_categories(D, cat_ranges):
    N_stim = D.shape[0]
    avg_dists = np.zeros(N_stim)

    for i in range(0, N_stim):
        other_cat_ranges = [r for r in cat_ranges if i not in r]
        avg_dists[i] = np.mean(D[i, other_cat_ranges])

    return avg_dists

def split_diff(SC, N_categories):
    D = distance_matrix(SC, SC)

    N_stim = SC.shape[0]
    N_diff_levels = 5

    cat_ranges = category_ranges(N_stim, N_categories)

    avg_dists = avg_dist_to_other_categories(D, cat_ranges)

    diffs = np.zeros(N_stim, dtype='i')
    c = 0
    for r in cat_ranges:
        cat_avgd = avg_dists[r]
        idxs = cat_avgd.argsort()[::-1] # sort by maximum average distance across other categories 
        idxs_diff = np.array_split(idxs, N_diff_levels)
        for j, dj in enumerate(idxs_diff):
            diffs[dj + c] = j
        c += len(r) 

    return diffs 

def write_shape(shape_ID, diff_level, category_ID, path_src, path_dest):
    os.makedirs(path_dest, exist_ok=True)
    c = len(os.listdir(path_dest))

    file_src = path_src + f'shape_{shape_ID}.png'
    file_dest =  path_dest + f'ex_{category_ID}_{diff_level}_{c+1}.png'

    shutil.copy(file_src, file_dest)

def write_shape_gif(shape_ID, prototype_ID, diff_level, category_ID, path_src, path_dest):
    s = np.sign(prototype_ID - shape_ID)
    files_src = [path_src + f'shape_{i}.png' for i in range(shape_ID, prototype_ID + s, s)]

    os.makedirs(path_dest, exist_ok=True)
    c = len(os.listdir(path_dest))

    frames = np.stack([iio.imread(f) for f in files_src], axis=0)
    filename =  path_dest + f'ex_{category_ID}_{diff_level}_{c+1}.gif'

    iio.imwrite(filename, frames, duration=150)
    optimize(filename)