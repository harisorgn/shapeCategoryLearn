import scipy.io as io

from utils import *

shape_set = 1
path_src = f'./shapes_{shape_set}/'
name_mat = 'shape_set360'

S = io.loadmat(path_src + 'shapes.mat')

shape_gif(S[name_mat], 190, 180, 1, 1, './')
