import numpy as np
import shutil
import os

from utils import *

shape_set = 3
path_src = f'./shapes_{shape_set}/'
SC = np.loadtxt(path_src + 'SC.txt', dtype='f', delimiter=',')

N_categories = 2
N_stim = SC.shape[0]

diffs = split_diff(SC, N_categories)
cat_ranges = category_ranges(N_stim, N_categories)

path_dest = f'./stimuli/pack_shapes_{shape_set}/'

for i, r in enumerate(cat_ranges):
    for ex in r[::2]:
        dir_dest = path_dest + f'cat_{i+1}/' + f'diff_{diffs[ex]+1}/'
        os.makedirs(dir_dest, exist_ok=True)
        c = len(os.listdir(dir_dest))

        file_src = path_src + f'shape_{ex+1}.png'
        file_dest =  dir_dest + f'ex_{i+1}_{diffs[ex]+1}_{c+1}.png'
        shutil.copy(file_src, file_dest)



