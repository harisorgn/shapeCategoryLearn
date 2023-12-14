import scipy.io as io

from utils import *

shape_set = 1
path_src = f'./shapes_{shape_set}/'
name_mat = 'shape_set360'

S = io.loadmat(path_src + 'shapes.mat')

#plot_shape(get_shape(S[name_mat], 180))

write_noise_shape_gif(S[name_mat], 50, 1, 1, './', fps=15, duration=5.5)
